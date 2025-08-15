import subprocess
import os

# Define the models and axes
models = ["bimba","duck", "bird", "fish",  "foot1", "foot2", "golden_retriever", "hand_fist",  "heart", "horse", "humerus", "kidney", "Lincoln", "lion",  "ok_hand_sign", "owl",
           "parrot", "pelvis", "pig", "rabbit",  "tooth", "torso", "turtle", "windfish", "wingspan", "shark", "bust", "frederick", "hand_point_prep", "skull"]


function_type = [ ("Height", "x"), ("Height", "y"), ("Height", "z"), ("Geodesic", "top"), ("Geodesic", "bottom"), ("Geodesic", "left"), ("Geodesic", "right"), ("Geodesic", "front"), ("Geodesic", "back")]

overwrite = True

# Path to the generate_reeb_graph script
script_path = "gasp_main.py"


def generate_rg(contour_spaces , contour_type ):
    for model in models:
        for ft, t in function_type:
            for nature_of_contour, buffer in contour_type:
                for space in contour_spaces:
                


                    input_path = f"Data/{ft}"
                    output_path = f"Output/{ft}/{nature_of_contour}/Contour_Space_{str(space)}/" + (f"Buffer_{str(buffer)}/" if buffer is not None else "")
                    debug_path = f"debug/{ft}/{nature_of_contour}-contour_space_{str(space)}" + (f"-buffer_{str(buffer)}" if buffer is not None else "") + f"/{model}_{t}/"

                    if os.path.exists(f"{output_path}/{model}_{t}.obj") and not overwrite:
                        continue
                    
                    print(f"Processing {model}_{t} with {nature_of_contour} contours, contour spacing {space}, buffer {buffer}...")

                    command = [
                        "python", script_path,
                        "--input_obj", f"{input_path}/{model}_{t}.obj",
                        "--input_rg", f"{input_path}/{model}_{t}_no_0_persistence.rg",
                        "--outputfile", f"{output_path}/{model}_{t}.obj",
                        "--method", nature_of_contour,
                        "--contour_spacing", space,
                        "--axis", t,
                        # "--debugging", debug_path,
                        "--parallel",
                    ]

                    if buffer is not None:
                        command += ["--buffer", str(buffer)]

                    subprocess.run(command)


###########BoundaryVSInterior#################
contour_spaces = ['0.05']
contour_type = [ ('boundary', None), ('interior', 0.05)]
##############################################
generate_rg(contour_spaces, contour_type)

###########ContourSpacing#####################
contour_type = [ ('boundary', None)]
contour_spaces = ['0.025', '0.05', '0.1']
##############################################
generate_rg(contour_spaces, contour_type)

###########Buffer############################
contour_type = [ ('interior', 0), ('interior', 0.025), ('interior', 0.05)]
contour_spaces = ['0.1']
##############################################
generate_rg(contour_spaces, contour_type)



print("Done processing all models and axes.")

