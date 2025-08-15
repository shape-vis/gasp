import argparse
import concurrent.futures

import GASP.cylinderReebGraph as cylinderReebGraph
import GASP.cutFeature as cutFeature
import GASP.contour as contour
import GASP.meshPreprocessor as meshPreprocessor

from GASP.cutConnectedComponents import cutConnectedComponents

import Utils.VertexContainer as VC

from Utils import FileIO
from Utils import Debugger
from Utils.Profiler import Profiler


#####################################
#####################################
#####################################

EPSILON = 0.0001
MESH_SLICES = 20

reebArc = []
feature_profilers = []

cutTriangleList = []

criticalPoints = None
criticalPointPairs = None
mesh = None

method = 'boundary'
contour_space = 0.05
buffer = 0
axis = "none"
# max_edge_len = 0.25
# max_subd_iso_loops = 5

#####################################
#####################################
#####################################

def procThinPair(cp_pair, is0persistence, fileNumber):

    profiler = Profiler(f'{"0-persistence" if is0persistence else "thin"} feature {cp_pair}').start()

    cut_profile = profiler.add_subprofiler('cut')
    if is0persistence:
        cutMesh = cutFeature.cutFeature0Persistence(mesh, cp_pair)
    else:
        cutMesh = cutFeature.cutFeature(cut_profile, mesh, criticalPoints, cp_pair, -EPSILON, True, fileNumber)
    cut_profile.stop()

    Debugger.writeMesh( f'cut/cut_{fileNumber}.obj', cutMesh )
    
    arc_profile = profiler.add_subprofiler('arc')
    thinArc = cylinderReebGraph.thinFeatureMethod( cutMesh, cp_pair, fileNumber)
    arc_profile.stop()

    reebArc.append(thinArc)

    

    profiler.stop()
    feature_profilers.append(profiler)

    cutTriangleList.append( (cp_pair[0], cp_pair[1], criticalPoints[cp_pair[0]][0], criticalPoints[cp_pair[1]][0], cutMesh.get_triangle_length()) )

    return 'zero' if is0persistence else 'thin', 1


def procRegularPair(cp_pair, fileNumber):
    profiler = Profiler(f'regular feature {cp_pair}').start()

    src, dst = cp_pair

    srcVal = criticalPoints[src][0]
    dstVal = criticalPoints[dst][0]    

    profile_cut = profiler.add_subprofiler('cut')
    cutMesh = cutFeature.cutFeature(profile_cut, mesh, criticalPoints, cp_pair, EPSILON, False, fileNumber)
    profile_cut.stop()

    profile_cc = profiler.add_subprofiler('connected components')
    ccTriangles = cutConnectedComponents( cutMesh, fileNumber)
    profile_cc.stop()

    cutVerts = cutMesh.get_dynamic_vertices()
    
    if len(ccTriangles) == 0:
        print(f'No valid connected components between critical points {src} and {dst}')

    for ccIdx, cc in enumerate(ccTriangles):
        profile_contour = profiler.add_subprofiler('contour')
        iso_array, contours = contour.createFixedContours( VC.VertexContainer(mesh.get_vertices(), cutVerts), cc, contour_space, srcVal + EPSILON, dstVal - EPSILON )
        profile_contour.stop()

        Debugger.writeContours(f'/contour/contour_{fileNumber}_cc_{ccIdx}', contours)
        
        profile_arc = profiler.add_subprofiler('arc')
        if method == 'boundary':
            cylinderArc = cylinderReebGraph.boundaryMethod(profile_arc, contours, cutMesh.get_vertex(src), cutMesh.get_vertex(dst), f'{fileNumber}_cc_{ccIdx}')
        elif method == 'interior':
            cylinderArc = cylinderReebGraph.interiorMethod(profile_arc, contours, cutMesh.get_vertex(src), cutMesh.get_vertex(dst), buffer, f'{fileNumber}_cc_{ccIdx}')
        else: 
            print("  ERROR: Invalid method value")     
            break   
        profile_arc.stop()


        reebArc.append(cylinderArc)

    profiler.stopall()
    feature_profilers.append(profiler)

    cutTriangleList.append( (src, dst, srcVal, dstVal, cutMesh.get_triangle_length())) 

    return 'regular', len(ccTriangles)
    

def procRgFile(threads=1):

    fileNumber = 0
    feature_count = {'zero': 0, 'thin': 0, 'regular': 0}

    pool = None if threads <= 1 else concurrent.futures.ThreadPoolExecutor(max_workers=threads)

    task = []
    res = []

    for cp_pair in criticalPointPairs:
        src, dst = cp_pair

        srcVal = criticalPoints[src][0]
        dstVal = criticalPoints[dst][0]

        Debugger.writeObj(f'cut/cut_{fileNumber}_{src}_{dst}_cp.obj', [ mesh.get_vertex(src), mesh.get_vertex(dst) ] )

        if abs(srcVal - dstVal) < contour_space:
            if pool is None:
                res.append( procThinPair(cp_pair, srcVal == dstVal, fileNumber) )
            else:
                task.append( pool.submit( procThinPair, cp_pair, srcVal == dstVal, fileNumber ) )
        else:
            if pool is None:
                res.append( procRegularPair(cp_pair, fileNumber) )
            else:
                task.append( pool.submit( procRegularPair, cp_pair, fileNumber ) )
                
        fileNumber += 1

    if pool is not None:
        pool.shutdown(wait=True)
        for t in task:
            res.append( t.result() )

    for r in res:
        type, count = r
        feature_count[type] += count

    return feature_count    


def saveRG(name):
    FileIO.writeRG_full(reebArc, f'{name[:-4]}.obj')
    



#####################################
#####################################
#####################################
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Example script with argparse")

    # Add arguments
    parser.add_argument("-i", "--input_obj", type=str, required=True, help="Input obj file name")
    parser.add_argument("-r", "--input_rg", type=str, required=True, help="Input rg file name")
    parser.add_argument("-o", "--outputfile", type=str, default=None, help="Output file name")
    parser.add_argument("-a", "--axis", type=str, default="x", help="Interior method axis")
    parser.add_argument("-c", "--contour_spacing", type=float, default=0.05, help="Contour spacing")
    parser.add_argument("-b", "--buffer", type=float, default=0, help="Buffer size")
    parser.add_argument("-m", "--method", type=str, default="boundary", help="Method type (interior or boundary)")
    parser.add_argument("-s", "--arc_smoothing", type=float, default=0, help="Arc smoothing distance")
    parser.add_argument("--debugging", type=str, default=None, help="Enable debugging to path")
    parser.add_argument("--performance", type=str, default=None, help="Enable performance profiling")
    parser.add_argument("--parallel", action="store_true", help="Enable parallel processing")

    # Parse arguments
    args = parser.parse_args()

    buffer = args.buffer
    contour_space = args.contour_spacing
    method = args.method
    axis = args.axis
    
    print()
    print('#############################################')
    print(f'  {args.input_obj}')
    print(f'  {args.input_rg}')

    if args.debugging is not None:
        Debugger.set_file_path(args.debugging)
        Debugger.set_enabled(True)

    profiler = Profiler('main').start()

    # Load the mesh and critical points
    print('################ LOADING ####################')
    profile_load = profiler.add_subprofiler('load')
    mesh = FileIO.readObj(args.input_obj, 'user')
    criticalPoints, criticalPointPairs = FileIO.readRGfile(args.input_rg)
    profile_load.stop()

    # Reeb Graph calculation
    profile_reebgraph = profiler.add_subprofiler('reeb graph')

    print('################ PREPROCESS #################')
    # # Preprocess the mesh by subdividing triangles that connect multiple critical points
    profile_preprocess = profile_reebgraph.add_subprofiler('mesh preprocess')
    mesh = meshPreprocessor.splitMultipleCriticalPointTriangles(mesh, criticalPoints, MESH_SLICES)
    profile_preprocess.stop()

    print('################ CALCULATING ################')
    # # calculate the Reeb graph arcs
    profile_reeb_calc = profile_reebgraph.add_subprofiler('arc calculation')
    feature_count = procRgFile( 8 if args.parallel else 1 )
    profile_reeb_calc.add_subprofiles(feature_profilers)
    profile_reeb_calc.stop()

    profile_reebgraph.stop()

    # Save the Reeb Graph
    if not args.outputfile is None:
        profile_save = profiler.add_subprofiler('save')
        saveRG(args.outputfile)
        profile_save.stop()
        profiler.stopall()

    # Print the summary
    print('################ SUMMARY ####################')
    print(f'  Total zero features: {feature_count["zero"]}')
    print(f'  Total thin featuers: {feature_count["thin"]}')
    print(f'  Total regular featuers: {feature_count["regular"]}')

    Debugger.writeString('profiler.txt', profiler.to_string())
    Debugger.writeString('profiler.json', profiler.to_json())
    if args.performance is not None:
        prof = { 'params': vars(args), 'profiler': profiler.to_dict(2), 'features': feature_count }
        FileIO.writeJson(args.performance, prof)        

    print('#############################################')
    print()



