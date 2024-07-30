from google.cloud import logging

def get_used_services(project_id, start_time, end_time):
    client = logging.Client(project=project_id)
    filter_str = f'timestamp >= "{start_time}" AND timestamp <= "{end_time}"'
    iterator = client.list_entries(filter_=filter_str)
    
    used_services = set()
    for entry in iterator:
        if 'protoPayload' in entry.payload:
            service_name = entry.payload['protoPayload']['serviceName']
            used_services.add(service_name)
    
    return used_services

project_id = 'YOUR_PROJECT_ID'
start_time = '2023-07-01T00:00:00Z'
end_time = '2023-07-30T23:59:59Z'

used_services = get_used_services(project_id, start_time, end_time)
print("実際に使用されているサービス:", used_services)
