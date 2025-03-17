import os 
from jinja2 import Environment,FileSystemLoader


def render_template(template_name, **kwargs):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    template_dir = os.path.join(current_dir, "templates")  
    
    env = Environment(loader=FileSystemLoader(template_dir))
    
    template = env.get_template(template_name)
    
    return template.render(**kwargs)