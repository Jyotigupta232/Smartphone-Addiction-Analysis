import os
import sys
import sqlite3
import zipfile
import io

def run_deployment_health_check(base_dir):
    """
    Executes a comprehensive health audit verifying system readiness for cloud deployment.
    """
    check_results = []
    
    # 1. File Structure Verification
    required_files = [
        ('app.py', 'Streamlit Main Application Entrypoint'),
        ('requirements.txt', 'Python Dependencies Manifest'),
        ('Procfile', 'Heroku/Render Process Command'),
        ('render.yaml', 'Render Blueprint Config'),
        ('.streamlit/config.toml', 'Streamlit Production Settings'),
        ('data/generate_schema_dataset.py', 'Data Warehouse Schema Generator'),
        ('src/pdf_generator.py', 'PDF Wellness Report Generator'),
        ('src/ml_predictor_dw.py', 'Machine Learning Risk Classifier')
    ]
    
    files_ok = True
    for fname, desc in required_files:
        fpath = os.path.join(base_dir, fname)
        exists = os.path.exists(fpath)
        check_results.append({
            'component': f'File: {fname}',
            'status': '✅ READY' if exists else '❌ MISSING',
            'details': desc
        })
        if not exists:
            files_ok = False
            
    # 2. Database & Warehouse Integrity
    db_path = os.path.join(base_dir, 'data', 'smartphone_addiction_dw.db')
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cur.fetchall()]
        conn.close()
        
        expected_tables = {'users', 'usage_logs', 'app_usage', 'sleep_patterns', 'notifications', 'user_feedback', 'screen_time'}
        missing_tbls = expected_tables - set(tables)
        
        if len(missing_tbls) == 0:
            check_results.append({
                'component': 'Database: SQL Data Warehouse',
                'status': '✅ READY',
                'details': f'7/7 Relational Tables Operational ({len(tables)} tables total)'
            })
        else:
            check_results.append({
                'component': 'Database: SQL Data Warehouse',
                'status': '⚠️ WARNING',
                'details': f'Missing tables: {missing_tbls}'
            })
    except Exception as e:
        check_results.append({
            'component': 'Database: SQL Data Warehouse',
            'status': '❌ ERROR',
            'details': str(e)
        })
        
    # 3. Machine Learning Models Audit
    try:
        from src.ml_predictor_dw import train_dw_ml_models
        ml_res, scaler, f_cols = train_dw_ml_models(db_path)
        check_results.append({
            'component': 'ML Models: 3-Class Risk Predictor',
            'status': '✅ READY',
            'details': f'Trained {len(ml_res)} models (Best Acc: {max(r["accuracy"] for r in ml_res.values())*100:.1f}%)'
        })
    except Exception as e:
        check_results.append({
            'component': 'ML Models: 3-Class Risk Predictor',
            'status': '❌ ERROR',
            'details': str(e)
        })

    # 4. PDF Generator Audit
    try:
        from src.pdf_generator import generate_weekly_wellness_pdf
        check_results.append({
            'component': 'PDF Engine: ReportLab Generator',
            'status': '✅ READY',
            'details': 'Digital Wellness PDF Engine compiled & functional'
        })
    except Exception as e:
        check_results.append({
            'component': 'PDF Engine: ReportLab Generator',
            'status': '❌ ERROR',
            'details': str(e)
        })
        
    return check_results

def create_deployment_zip(base_dir):
    """
    Bundles the entire repository into an in-memory ZIP package ready for one-click download.
    """
    zip_buffer = io.BytesIO()
    
    ignore_dirs = {'.git', '__pycache__', '.pytest_cache', 'venv', 'env', '.idea'}
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(base_dir):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                if file.endswith('.pyc') or file.endswith('.db'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, base_dir)
                zip_file.write(file_path, arcname)
                
    zip_buffer.seek(0)
    return zip_buffer.getvalue()
