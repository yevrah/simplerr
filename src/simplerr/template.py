from jinja2 import Environment, FileSystemLoader


class Template(object):
    def __init__(self, cwd):
        self.cwd = cwd
        self.env = Environment(loader=FileSystemLoader(cwd), autoescape=True)

    def render(self, template, data={}):
        return self.env.get_template(template).render(**data)


# TODO: Remove when rest is updated
T = Template
