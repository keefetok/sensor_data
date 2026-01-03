OOP principles:

1. Encapsulation: no direct access to data from outside of Class, functions and
data hidden in class.

e.g

class DataCache:
    def __init__(self):
        self._cache = {}  # Private attribute (convention with _)
    
    def get(self, key):
        return self._cache.get(key)  # Controlled access
    
    def set(self, key, value):
        self._cache[key] = value

cache is private, and must use get() method

@staticmethod in visualizer (this was with AI help)

2. Abstraction: Hide complex implementation

e.g simple connect --> load --> return: 
    df = self.loader.load_sensor_data(sensor_id)


3. Inheritance: Never implement inheritance

4. Polymorphism: Allow single interface to represent different underlying types
--> loader.load_sensor_data() should be programmed to work with any loader 
    instead of current case where it is azure loader only, in case of different
    cloud service provider use --> Can use loader for AWS S3 instead. 

===============================================================================
Streamlit used because of local deploy and quick testing to ensure I meet
requirements set for the task. Allows me to deploy using docker.