
try:
    with open('backend/auc_synthetic_results.txt', 'r', encoding='utf-16') as f:
        content = f.read()
        print(content[-2000:])
except Exception as e:
    # print(f"Error reading utf-16: {e}")
    try:
        with open('backend/auc_synthetic_results.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            print(content[-2000:])
    except Exception as e2:
        print(f"Error reading utf-8: {e2}")
