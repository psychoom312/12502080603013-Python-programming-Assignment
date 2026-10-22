import sys

def optimize_matrix_path():
    input_data = sys.stdin.read().splitlines()
    if not input_data:
        return

    first_line = input_data[0].split()
    n = int(first_line[0])
    m = int(first_line[1])
    
    MOD = 1000000007
    
    # Initialize DP tables for space complexity O(m)
    # prev_score and prev_paths track values from the previous row
    prev_score = [float('-inf')] * m
    prev_paths = [0] * m
    
    # Read row 0
    row0 = input_data[1].split()
    if row0[0] != 'X':
        prev_score[0] = int(row0[0])
        prev_paths[0] = 1
        
    for j in range(1, m):
        if row0[j] == 'X' or prev_score[j-1] == float('-inf'):
            continue
        prev_score[j] = prev_score[j-1] + int(row0[j])
        prev_paths[j] = prev_paths[j-1]

    # Process subsequent rows
    for i in range(1, n):
        curr_score = [float('-inf')] * m
        curr_paths = [0] * m
        row_vals = input_data[i+1].split()
        
        for j in range(m):
            if row_vals[j] == 'X':
                continue
                
            cell_score = int(row_vals[j])
            max_s = float('-inf')
            
            # Check up (from prev_score[j])
            if prev_score[j] > max_s:
                max_s = prev_score[j]
                
            # Check left (from curr_score[j-1])
            if j > 0 and curr_score[j-1] > max_s:
                max_s = curr_score[j-1]
                
            # Check diagonal (from prev_score[j-1])
            if j > 0 and prev_score[j-1] > max_s:
                max_s = prev_score[j-1]
                
            if max_s == float('-inf'):
                continue
                
            curr_score[j] = max_s + cell_score
            paths_sum = 0
            
            if prev_score[j] == max_s:
                paths_sum = (paths_sum + prev_paths[j]) % MOD
            if j > 0 and curr_score[j-1] == max_s:
                paths_sum = (paths_sum + curr_paths[j-1]) % MOD
            if j > 0 and prev_score[j-1] == max_s:
                paths_sum = (paths_sum + prev_paths[j-1]) % MOD
                
            curr_paths[j] = paths_sum

        prev_score = curr_score
        prev_paths = curr_paths

    if prev_score[m-1] == float('-inf'):
        print("IMPOSSIBLE")
    else:
        print(f"{prev_score[m-1]} {prev_paths[m-1]}")

if __name__ == "__main__":
    optimize_matrix_path()
