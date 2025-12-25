import traceback
import sys
import os

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from services.upload_service import upload_service
    from services.image_service import ImageAnalysisService
    from services.office_service import OfficeAnalysisService
    from routes.analysis import analysis_bp
    print('IMPORTS_OK')
except Exception as e:
    traceback.print_exc()
    print('IMPORT_FAILED', e)
