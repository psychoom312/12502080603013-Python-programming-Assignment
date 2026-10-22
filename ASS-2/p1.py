import re
import sys

def extract_email_intelligence(file_path):
    email_pattern = re.compile(r'\b[a-zA-Z0-9+._-]+@([a-zA-Z0-9.-]+\.(?:com|edu|org))\b')
    domain_data = {}

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                for match in email_pattern.finditer(line):
                    full_email = match.group(0)
                    domain = match.group(1).lower()
                    
                    if domain not in domain_data:
                        domain_data[domain] = set()
                    
                    domain_data[domain].add(full_email)
                    
    except FileNotFoundError:
        return

    for domain in sorted(domain_data.keys()):
        emails_set = domain_data[domain]
        unique_user_count = len(emails_set)
        smallest_email = min(emails_set)
        
        print(f"{domain} {unique_user_count} {smallest_email}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        extract_email_intelligence(sys.argv[1])
