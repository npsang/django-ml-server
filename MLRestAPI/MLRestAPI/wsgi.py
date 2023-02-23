import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MLRestAPI.settings')

application = get_wsgi_application()

# ML Registry
from ml.registry import MLRegistry
from ml.compute_similarity.vien_cross_similarity import ViEnCrossSimilarity
from ml.compute_similarity.vietnamese_similarity import VietnameseSimilarity
from ml.compute_similarity.english_similarity import EnglishSimilarity
from ml.translate.translate import Translate
try: 
    # create ML registry
    registry = MLRegistry()
    # Vietnamese Compute Similarity Model
    vi = VietnameseSimilarity()
    registry.add_algorithm(
        algorithm_name='Vietnamese Compute Similarity',
        algorithm_object=vi,
        acronym='vi',
        algorithm_description="Model for compute Vietnamese document similarity",
        algorithm_version='0.0.1',
        owner='dev1'
        )
    print(f'Registry VietnameseSimilarity success: {registry.models["vi"]}')
    
    #  English Compute Similarity Model
    en = EnglishSimilarity()
    registry.add_algorithm(
        algorithm_name='English Compute Similarity',
        algorithm_object=en,
        acronym='en',
        algorithm_description="Model for compute English document similarity",
        algorithm_version='0.0.1',
        owner='dev1'
        )
    print(f'Registry EnglishSimilarity success: {registry.models["en"]}')

    # Vietnamese English Cross Compute Similarity Model
    cross = ViEnCrossSimilarity()
    registry.add_algorithm(
        algorithm_name='Vietnamese English Cross Compute Similarity',
        algorithm_object=cross,
        acronym='cross',
        algorithm_description="Model for compute crossed Vietnamese-English document similarity",
        algorithm_version='0.0.1',
        owner='dev1'
        )

    print(f'Registry ViEnCrossSimilarity success: {registry.models["cross"]}')
    # Translate
    translate = Translate()
    registry.add_algorithm(
        algorithm_name='Vietnamese English Translate',
        algorithm_object=translate,
        acronym='translate',
        algorithm_description="Model for translate vietnames to english text or english text to vietnamese text",
        algorithm_version='0.0.1',
        owner='dev1'
    )
    print(f'Registry Vietnamese English Translate success: {registry.models["translate"]}')

except Exception as e:
    print("Exception while loading the algorithm to registry,",str(e))