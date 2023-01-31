from app.models import MLModel


class MLRegistry:
    
    def __init__(self):
        self.model = {}

    def add_algorithm(self, algorithm_name, algorith_description, algorithm_version,owner, algorithm_object):
        database_object, _ = MLModel.objects.get_or_create(
            name=algorithm_name,
            description=algorith_description,
            version=algorithm_version,
            owner=owner,
        )
        self.model[database_object.id] = algorithm_object

        