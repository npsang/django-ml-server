import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MLRestAPI.settings')

application = get_wsgi_application()

# ML Registry
from ml.registry import MLRegistry
from ml.compute_similarity.compute_similarity import ComputeSimilarity

try: 
    # create ML registry
    registry = MLRegistry()
    # Compute Similarity Model
    cs = ComputeSimilarity()
    registry.add_algorithm(algorithm_name='Compute Similarity',
                            algorithm_object=cs,
                            algorith_description="model for compute document similarity",
                            algorithm_version='0.0.1',
                            owner='dev1'
                            )
    print(registry.model)
except Exception as e:
    print("Exception while loading the algorithm to registry,",str(e))