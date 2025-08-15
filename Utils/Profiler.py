import time
import json

class Profiler:
    def __init__(self, name):
        self.name = name
        self.start_time = None
        self.total_time = 0.0
        self.subprofilers = []
    
    def start(self):
        """Start the timer."""
        if self.start_time is not None:
            raise RuntimeError(f"Timer '{self.name}' is already running.")
        self.start_time = time.time()
        return self
    
    def stop(self):
        """Stop the timer."""
        if self.start_time is None:
            raise RuntimeError(f"Timer '{self.name}' has not been started.")
        elapsed = time.time() - self.start_time
        self.total_time += elapsed
        self.start_time = None
        return self

    def stopall(self):
        """Stop the timer and all subtimers."""
        if not self.start_time is None:
            elapsed = time.time() - self.start_time
            self.total_time += elapsed
            self.start_time = None    
        for subprofiler in self.subprofilers:    
            subprofiler.stopall()
        return self
    
    def add_subprofiler(self, subprofiler_name, start=True):
        """Add or get a subtimer by name."""
        subprofiler = Profiler(subprofiler_name)
        self.subprofilers.append(subprofiler)
        if start:
            subprofiler.start()
        return subprofiler

    def add_subprofiles(self, subprofiler_list ):
        """Add a list of subtimers."""
        for subprofiler in subprofiler_list:
            self.subprofilers.append(subprofiler)
        return self

    def print_report(self, indent=0):
        """Prints a report of the timer and its subtimers."""
        indent_str = '    ' * indent
        print(f"{indent_str}Timer '{self.name}': {self.total_time:.6f} seconds")
        for subprofiler in self.subprofilers:
            subprofiler.print_report(indent + 1)
    
    def to_dict(self, max_depth=999):
        """Convert the timer and its subtimers to a dictionary format."""
        result = {
            'name': self.name,
            'total_time': self.total_time,
        }
        if max_depth > 1:
            result['subprofilers'] = [subprofiler.to_dict(max_depth - 1) for subprofiler in self.subprofilers]
        return result
    
    def to_json(self, max_depth=999):
        """Convert the timer and its subtimers to a JSON string."""
        return json.dumps(self.to_dict(max_depth), indent=2)

    def to_string(self, indent=0):
        """Convert the timer and its subtimers to a string."""
        indent_str = '    ' * indent
        ret = f"{indent_str}Timer '{self.name}': {self.total_time:.6f} seconds\n"
        for subprofiler in self.subprofilers:
            ret += subprofiler.to_string(indent + 1)
        return ret
