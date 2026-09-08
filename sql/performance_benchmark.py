import os
import time
import sqlite3
import pandas as pd

def run_performance_benchmarks():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    db_path = os.path.join(data_dir, 'smartphone_addiction.db')
    
    survey_csv = os.path.join(data_dir, 'smartphone_addiction_dataset.csv')
    sessions_csv = os.path.join(data_dir, 'app_usage_sessions.csv')
    
    # Generate data if missing
    if not os.path.exists(survey_csv) or not os.path.exists(sessions_csv):
        print("Dataset missing. Executing generate_dataset.py...")
        import sys
        sys.path.append(base_dir)
        from data.generate_dataset import generate_survey_dataset, generate_usage_sessions_dataset
        survey_df = generate_survey_dataset(2500)
        sessions_df = generate_usage_sessions_dataset(survey_df, 100000)
        survey_df.to_csv(survey_csv, index=False)
        sessions_df.to_csv(sessions_csv, index=False)
    else:
        survey_df = pd.read_csv(survey_csv)
        sessions_df = pd.read_csv(sessions_csv)
        
    print(f"Loaded Survey Dataset ({len(survey_df)} rows) & Session Logs ({len(sessions_df)} rows)")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read and apply schema
    schema_path = os.path.join(base_dir, 'sql', 'schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    conn.commit()
    
    # Load into tables
    print("Populating SQLite Database tables...")
    survey_df.to_sql('users_survey', conn, if_exists='replace', index=False)
    sessions_df.to_sql('app_usage_sessions_unindexed', conn, if_exists='replace', index=False)
    sessions_df.to_sql('app_usage_sessions_indexed', conn, if_exists='replace', index=False)
    
    # Create indexes on indexed table explicitly
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON app_usage_sessions_indexed(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_cat ON app_usage_sessions_indexed(app_category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_app_dur ON app_usage_sessions_indexed(app_name, session_duration_min);")
    conn.commit()
    
    # Benchmark 1: User Lookup & Aggregation
    user_id_test = survey_df['User_ID'].iloc[50]
    query_unindexed = f"SELECT user_id, COUNT(*), SUM(session_duration_min) FROM app_usage_sessions_unindexed WHERE user_id = '{user_id_test}' GROUP BY user_id;"
    query_indexed = f"SELECT user_id, COUNT(*), SUM(session_duration_min) FROM app_usage_sessions_indexed WHERE user_id = '{user_id_test}' GROUP BY user_id;"
    
    print("\n" + "="*70)
    print("  SQL QUERY PERFORMANCE BENCHMARK (100,000+ RECORDS) - XENO OPTIMIZATION")
    print("="*70)
    
    # Timing Unindexed
    t0 = time.perf_counter()
    cursor.execute(query_unindexed)
    res_unindexed = cursor.fetchall()
    t_unindexed = (time.perf_counter() - t0) * 1000.0
    
    # Timing Indexed
    t0 = time.perf_counter()
    cursor.execute(query_indexed)
    res_indexed = cursor.fetchall()
    t_indexed = (time.perf_counter() - t0) * 1000.0
    
    # Query Plans
    cursor.execute(f"EXPLAIN QUERY PLAN {query_unindexed}")
    plan_unindexed = cursor.fetchall()
    
    cursor.execute(f"EXPLAIN QUERY PLAN {query_indexed}")
    plan_indexed = cursor.fetchall()
    
    speedup = t_unindexed / t_indexed if t_indexed > 0 else 1.0
    
    print(f"\n[QUERY 1] Single User Aggregation Lookup for '{user_id_test}':")
    print(f"  • Unindexed Execution Time : {t_unindexed:.3f} ms")
    print(f"  • Indexed Execution Time   : {t_indexed:.3f} ms")
    print(f"  • Performance Speedup Ratio: {speedup:.2f}x Faster!")
    print(f"\n  • Unindexed Query Plan     : {plan_unindexed[0][3] if plan_unindexed else 'SCAN TABLE'}")
    print(f"  • Indexed Query Plan       : {plan_indexed[0][3] if plan_indexed else 'SEARCH TABLE USING INDEX'}")
    
    # Benchmark 2: Category Filter & Duration Aggregate
    cat_query_unindexed = "SELECT app_category, AVG(session_duration_min) FROM app_usage_sessions_unindexed WHERE app_category = 'Social Media' GROUP BY app_category;"
    cat_query_indexed = "SELECT app_category, AVG(session_duration_min) FROM app_usage_sessions_indexed WHERE app_category = 'Social Media' GROUP BY app_category;"
    
    t0 = time.perf_counter()
    cursor.execute(cat_query_unindexed)
    cursor.fetchall()
    t_cat_unindexed = (time.perf_counter() - t0) * 1000.0
    
    t0 = time.perf_counter()
    cursor.execute(cat_query_indexed)
    cursor.fetchall()
    t_cat_indexed = (time.perf_counter() - t0) * 1000.0
    
    print(f"\n[QUERY 2] Category Aggregation ('Social Media'):")
    print(f"  • Unindexed Execution Time : {t_cat_unindexed:.3f} ms")
    print(f"  • Indexed Execution Time   : {t_cat_indexed:.3f} ms")
    print(f"  • Performance Speedup Ratio: {t_cat_unindexed/max(t_cat_indexed, 0.001):.2f}x Faster!")
    print("="*70 + "\n")
    
    conn.close()
    return {
        'user_id': user_id_test,
        'unindexed_time_ms': t_unindexed,
        'indexed_time_ms': t_indexed,
        'speedup': speedup,
        'unindexed_plan': plan_unindexed[0][3] if plan_unindexed else '',
        'indexed_plan': plan_indexed[0][3] if plan_indexed else ''
    }

if __name__ == '__main__':
    run_performance_benchmarks()
