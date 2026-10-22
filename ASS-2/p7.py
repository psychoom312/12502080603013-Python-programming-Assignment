import json
import sys

def read_jsonl(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    yield line
    except FileNotFoundError:
        return

def transform_and_validate(lines):
    for line in lines:
        try:
            data = json.loads(line)
            if 'device_id' not in data or 'temperature_c' not in data:
                yield None, None
                continue
                
            device_id = data['device_id']
            temp_raw = data['temperature_c']
            
            if isinstance(temp_raw, (int, float)) and not isinstance(temp_raw, bool):
                yield device_id, float(temp_raw)
            elif isinstance(temp_raw, str):
                try:
                    yield device_id, float(temp_raw)
                except ValueError:
                    yield device_id, None
            else:
                yield device_id, None
        except json.JSONDecodeError:
            yield None, None

def run_etl_pipeline(file_path):
    lines_gen = read_jsonl(file_path)
    records_gen = transform_and_validate(lines_gen)
    
    device_metrics = {}
    
    for device_id, temp in records_gen:
        if device_id is None:
            continue
            
        if device_id not in device_metrics:
            device_metrics[device_id] = {
                'count': 0,
                'min': float('inf'),
                'max': float('-inf'),
                'sum': 0.0,
                'corrupted': 0
            }
            
        metrics = device_metrics[device_id]
        
        if temp is None:
            metrics['corrupted'] += 1
        else:
            metrics['count'] += 1
            metrics['sum'] += temp
            if temp < metrics['min']:
                metrics['min'] = temp
            if temp > metrics['max']:
                metrics['max'] = temp

    for device in sorted(device_metrics.keys()):
        m = device_metrics[device]
        if m['count'] > 0:
            avg_temp = m['sum'] / m['count']
            print(f"{device} count={m['count']} min={int(m['min']) if m['min'].is_integer() else m['min']} max={int(m['max']) if m['max'].is_integer() else m['max']} avg={avg_temp:.2f} corrupted={m['corrupted']}")
        else:
            print(f"{device} count=0 min=N/A max=N/A avg=N/A corrupted={m['corrupted']}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_etl_pipeline(sys.argv[1])
