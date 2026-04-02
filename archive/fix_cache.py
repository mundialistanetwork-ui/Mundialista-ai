with open('prediction_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'def clear_cache' not in content:
    func = '''

def clear_cache():
    global _results_cache, _rankings_cache, _goalscorers_cache
    _results_cache = None
    _rankings_cache = None
    _goalscorers_cache = None

'''
    marker = 'def get_all_teams'
    idx = content.find(marker)
    if idx > -1:
        content = content[:idx] + func + content[idx:]
        print("Added clear_cache()")
    else:
        content += func
        print("Added clear_cache() at end")
    
    with open('prediction_engine.py', 'w', encoding='utf-8') as f:
        f.write(content)
else:
    print("clear_cache already exists")
