import hcl2
import boto3

def parse_terraform_file(file_path):
    with open(file_path, 'r') as file:
        tf_config = hcl2.load(file)
    return tf_config

def list_ec2_instances():
    ec2 = boto3.client('ec2')
    instances = ec2.describe_instances()
    region = ec2.meta.region_name  # Retrieve the region name from the client metadata
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance['Region'] = region  # Append region to each instance
    return instances

def list_rds_instances():
    rds = boto3.client('rds')
    instances = rds.describe_db_instances()
    region = rds.meta.region_name  # Retrieve the region name from the client metadata
    db_instances = []
    for db_instance in instances['DBInstances']:
        db_instance['Region'] = region
        db_instances.append(db_instance)
    return {'DBInstances': db_instances}

def list_lambda_functions():
    lambda_client = boto3.client('lambda')
    functions = lambda_client.list_functions()
    return functions

def list_s3_buckets():
    s3 = boto3.client('s3')
    buckets = s3.list_buckets()
    return buckets

def parse_aws_s3_buckets(aws_output_s3):
    aws_s3_buckets = []
    for bucket in aws_output_s3['Buckets']:
        aws_s3_buckets.append({
            'name': bucket['Name'],
            'creation_date': bucket['CreationDate'],
        })
    return aws_s3_buckets

def parse_aws_lambda_functions(aws_output_lambda):
    aws_lambda_functions = []
    for function in aws_output_lambda['Functions']:
        aws_lambda_functions.append({
            'name': function['FunctionName'],
            'runtime': function['Runtime'],
            'memory': function['MemorySize'],
        })
    return aws_lambda_functions

def parse_tf_lambda(terraform_output):
    terraform_lambda_functions = [
        {
            'name': resource['aws_lambda_function'][name]['function_name'],
            'runtime': resource['aws_lambda_function'][name]['runtime'],
            'memory': resource['aws_lambda_function'][name]['memory_size'],
            'region': terraform_output['provider'][0]['aws']['region']
        }
        for resource in terraform_output['resource']
        if 'aws_lambda_function' in resource  # Check if 'aws_lambda_function' key exists
        for name in resource['aws_lambda_function']
    ]
    return terraform_lambda_functions

def parse_aws_rds(aws_output_rds):
    aws_rds_instances = []
    for db_instance in aws_output_rds['DBInstances']:
        db_instance_name = next((tag['Value'] for tag in db_instance.get('TagList', []) if tag['Key'] == 'Name'), 'Unnamed RDS')
        aws_rds_instances.append({
            'db_instance_class': db_instance['DBInstanceClass'],
            'engine': db_instance['Engine'],
            'db_name': db_instance.get('DBName', 'Unnamed'),
            'name': db_instance_name,
            'region': db_instance['Region']
        })
        
    return aws_rds_instances

def parse_aws_ec2(aws_output_ec2):
    aws_instances = []
    for reservation in aws_output_ec2['Reservations']:
        for instance in reservation['Instances']:
            instance_name = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'Unnamed')
            aws_instances.append({
                'ami': instance['ImageId'],
                'instance_type': instance['InstanceType'],
                'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])},
                'name': instance_name,
                'region': instance['Region']
            })
            
    return aws_instances

def parse_tf_rds_instances(terraform_output):
    terraform_rds_instances = [
        {
            'db_instance_class': resource['aws_db_instance'][name]['instance_class'],
            'engine': resource['aws_db_instance'][name]['engine'],
            'db_name': resource['aws_db_instance'][name].get('db_name', 'Unnamed RDS'),
            'name': resource['aws_db_instance'][name]['tags'].get('Name', 'Unnamed RDS'),
            'region': terraform_output['provider'][0]['aws']['region']
        }
        for resource in terraform_output['resource']
        if 'aws_db_instance' in resource  # Check if 'aws_db_instance' key exists
        for name in resource['aws_db_instance']
    ]
    
    return terraform_rds_instances

def parse_tf_ec2_instances(terraform_output):
    terraform_instances = [
        {
            'ami': resource['aws_instance'][name]['ami'],
            'name': resource['aws_instance'][name]['tags'].get('Name', 'Unnamed'),
            'instance_type': resource['aws_instance'][name]['instance_type'],
            'tags': resource['aws_instance'][name]['tags'],
            'region': terraform_output['provider'][0]['aws']['region']
        }
        for resource in terraform_output['resource']
        if 'aws_instance' in resource  # Check if 'aws_instance' key exists
        for name in resource['aws_instance']
    ]
    
    return terraform_instances

def parse_tf_s3_buckets(terraform_output):
    terraform_s3_buckets = [
        {
            'name': resource['aws_s3_bucket'][name]['bucket'],
            'region': terraform_output['provider'][0]['aws']['region']
        }
        for resource in terraform_output['resource']
        if 'aws_s3_bucket' in resource
        for name in resource['aws_s3_bucket']
    ]
    
    return terraform_s3_buckets

def generate_report(terraform_output, aws_output_ec2, aws_output_rds, aws_output_lambda, aws_output_s3):
    ec2_icon_url = 'https://miro.medium.com/v2/resize:fit:300/0*feclcsOioZtq8ceI.png'  
    rds_icon_url = 'https://newrelic.com/sites/default/files/quickstarts/images/icons/aws-rds--logo.svg'  
    lambda_icon_url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTBmTsbyIoAIBzCzjk334X8fh4YnqOsomM_Prm5uXjklA&s' 
    s3_icon_url= 'https://seeklogo.com/images/A/amazon-s3-simple-storage-service-logo-9A3F37976E-seeklogo.com.png'
    html_report = []

    terraform_instances = parse_tf_ec2_instances(terraform_output)
    terraform_rds_instances = parse_tf_rds_instances(terraform_output)
    terraform_lambda_functions = parse_tf_lambda(terraform_output)
    terraform_s3_buckets = parse_tf_s3_buckets(terraform_output)

    aws_ec2_instances = parse_aws_ec2(aws_output_ec2)
    aws_rds_instances = parse_aws_rds(aws_output_rds)
    aws_lambda_functions = parse_aws_lambda_functions(aws_output_lambda)
    aws_s3_buckets = parse_aws_s3_buckets(aws_output_s3)

    deployed_ec2 = []
    missing_ec2 = []

    for tf_instance in terraform_instances:
        match_found = False
        for aws_instance in aws_ec2_instances:
            if (tf_instance['ami'] == aws_instance['ami'] and
                tf_instance['instance_type'] == aws_instance['instance_type'] and
                tf_instance['tags'] == aws_instance['tags'] and
                tf_instance['region'] == aws_instance['region']):
                deployed_ec2.append(f"<img src='{ec2_icon_url}' alt='EC2 Icon' class='ec2-icon'><b>EC2</b> {tf_instance['name']} in {tf_instance['region']} with AMI {tf_instance['ami']} and type {tf_instance['instance_type']}")
                match_found = True
                break
        if not match_found:
            missing_ec2.append(f"<img src='{ec2_icon_url}' alt='EC2 Icon' class='ec2-icon'><b>EC2</b> {tf_instance['name']} in {tf_instance['region']} with AMI {tf_instance['ami']} and type {tf_instance['instance_type']}")

    # Compare RDS Instances
    deployed_rds = []
    missing_rds = []
    for tf_db in terraform_rds_instances:
        match_found = False
        for aws_db in aws_rds_instances:
            print(tf_db)
            print(aws_db)
            if (tf_db['db_instance_class'] == aws_db['db_instance_class'] and
                tf_db['engine'] == aws_db['engine'] and
                tf_db['name'] == aws_db['name']):
                deployed_rds.append(f"<img src='{rds_icon_url}' alt='RDS Icon' class='rds-icon'><b>RDS</b> {tf_db['name']} in {tf_db['region']} with engine {tf_db['engine']} and class {tf_db['db_instance_class']}")
                match_found = True
                break
        if not match_found:
            missing_rds.append(f"<img src='{rds_icon_url}' alt='RDS Icon' class='rds-icon'><b>RDS</b> {tf_db['name']} in {tf_db['region']} with engine {tf_db['engine']} and class {tf_db['db_instance_class']}")

    deployed_lambda = []
    missing_lambda = []
    for tf_lambda in terraform_lambda_functions:
        match_found = False
        for aws_lambda in aws_lambda_functions:
            if tf_lambda['name'] == aws_lambda['name']:
                deployed_lambda.append(f"<img src='{lambda_icon_url}' alt='RDS Icon' class='rds-icon'><b>Lambda</b> {tf_lambda['name']} in {tf_lambda['region']} with runtime {tf_lambda['runtime']} and memory {tf_lambda['memory']}")
                match_found = True
                break
        if not match_found:
            missing_lambda.append(f"<img src='{lambda_icon_url}' alt='RDS Icon' class='rds-icon'><b>Lambda</b> {tf_lambda['name']} in {tf_lambda['region']} with runtime {tf_lambda['runtime']} and memory {tf_lambda['memory']}")

    deployed_s3 = []
    missing_s3 = []
    for tf_s3 in terraform_s3_buckets:
        match_found = False
        for aws_s3 in aws_s3_buckets:
            if tf_s3['name'] == aws_s3['name']:
                deployed_s3.append(f"<img src='{s3_icon_url}' alt='RDS Icon' class='rds-icon'><b>S3</b> {tf_s3['name']} in {tf_s3['region']}")
                match_found = True
                break
        if not match_found:
            missing_s3.append(f"<img src='{s3_icon_url}' alt='RDS Icon' class='rds-icon'><b>S3</b> {tf_s3['name']} in {tf_s3['region']}")
    


    html_report.append('<button class="collapsible missing-button">Missing Services <span class="collapsible-icon">&#9660;</span></button><div class="content"><ul>')
    for service in missing_ec2:
        html_report.append(f"<li class='missing'>{service}</li>")
    for service in missing_rds:
        html_report.append(f"<li class='missing'>{service}</li>")
    for lambda_function in missing_lambda:
        html_report.append(f"<li class='missing'>{lambda_function}</li>")
    for s3_bucket in missing_s3:
        html_report.append(f"<li class='missing'>{s3_bucket}</li>")
    html_report.append('</ul></div>')

    html_report.append('<button class="collapsible ok-button">Deployed Services <span class="collapsible-icon">&#9660;</span></button><div class="content"><ul>')
    for service in deployed_ec2:
        html_report.append(f"<li class='ok'>{service}</li>")
    for service in deployed_rds:
        html_report.append(f"<li class='ok'>{service}</li>")
    for lambda_function in deployed_lambda:
        html_report.append(f"<li class='ok'>{lambda_function}</li>")
    for s3_bucket in deployed_s3:
        html_report.append(f"<li class='ok'>{s3_bucket}</li>")
    html_report.append('</ul></div>')


    return '\n'.join(html_report)


def generate_html_report(terraform_resources, aws_resources_ec2, aws_output_rds, aws_output_lambda, aws_output_s3):
    report_content = generate_report(terraform_resources, aws_resources_ec2, aws_output_rds, aws_output_lambda, aws_output_s3)
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Post-Deploy Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Roboto', sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .ec2-icon, .rds-icon {{
            height: 24px;
            width: 24px; /* Set a fixed width */
            vertical-align: middle;
            margin-right: 5px;
        }}
        hr.gradient {{
          height: 3px;
          border: none;
          border-radius: 6px;
          background: linear-gradient(
            90deg,
            rgba(13, 8, 96, 1) 0%,
            rgba(9, 9, 121, 1) 21%,
            rgba(6, 84, 170, 1) 51%,
            rgba(0, 255, 113, 1) 100%
          );
        }}       
        .container {{
            max-width: 800px;
            margin: auto;
            padding: 20px;
            background-color: #fff;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            font-size: 24px;
            font-weight: bold;
        }}
        .collapsible {{
            background-color: #008cba;
            color: white;
            cursor: pointer;
            padding: 18px;
            width: 100%;
            border: none;
            text-align: left;
            outline: none;
            font-size: 15px;
            transition: background-color 0.3s;
            border-radius: 5px;
            margin-top: 10px;
        }}
        .missing-button {{
            background-color: #dc3545;
        }}
        .ok-button {{
            background-color: #28a745;
        }}
        .collapsible:hover, .collapsible.active {{
            background-color: #005f73;
        }}
        .collapsible-icon {{
            float: right;
            transition: transform 0.3s;
        }}
        .collapsible.active .collapsible-icon {{
            transform: rotate(-180deg);
        }}
        .content {{
            padding: 0 18px;
            display: none;
            overflow: hidden;
            background-color: #f9f9f9;
            transition: max-height 0.2s ease-out;
            margin-bottom: 10px;
            border-radius: 5px;
        }}
        ul {{
            list-style-type: none;
            padding: 0;
        }}
        li {{
            padding: 10px;
            margin-top: 5px;
            background-color: #eee;
            border-radius: 5px;
        }}
        .ok {{
            background-color: #d4edda;
            color: #155724;
        }}
        .missing {{
            background-color: #f8d7da;
            color: #721c24;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>AWS Deploy Report</h1>
        <hr class="gradient">
        {report_content}
    </div>
    <script>
        var coll = document.getElementsByClassName("collapsible");
        var i;

        for (i = 0; i < coll.length; i++) {{
            coll[i].addEventListener("click", function() {{
                this.classList.toggle("active");
                var content = this.nextElementSibling;
                if (content.style.display === "block") {{
                    content.style.display = "none";
                }} else {{
                    content.style.display = "block";
                }}
                var icon = this.children[0];
                icon.style.transform = icon.style.transform === 'rotate(-180deg)' ? 'rotate(0deg)' : 'rotate(-180deg)';
            }});
        }}
    </script>
</body>
</html>
"""
    with open("index.html", "w") as file:
        file.write(html_template)

terraform_resources = parse_terraform_file('./terraform/main.tf')
aws_resources_ec2 = list_ec2_instances()
aws_resources_rds = list_rds_instances()
aws_resources_lambda = list_lambda_functions()
aws_resources_s3 = list_s3_buckets()


generate_html_report(terraform_resources, aws_resources_ec2, aws_resources_rds, aws_resources_lambda, aws_resources_s3)
