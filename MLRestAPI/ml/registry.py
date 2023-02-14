from app.models import MLModel


class MLRegistry:
    
    def __init__(self):
        self.models = {}

    def add_algorithm(self,
    algorithm_name,
    acronym,
    algorithm_description,
    algorithm_version,
    owner,
    algorithm_object):
        database_object, _ = MLModel.objects.get_or_create(
            name=algorithm_name,
            acronym=acronym,
            description=algorithm_description,
            version=algorithm_version,
            owner=owner,
        )
        self.models[database_object.acronym] = algorithm_object
        