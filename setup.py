from setuptools import setup, find_packages

setup(name="UNComtrade",
      packages=["my_code", "my_code.Orange_widget.orange_widget"],
      package_data={"orange_widget": ["icons/*.svg", "icons/*.jpg"]},
      classifiers=["Example :: Invalid"],
      # Declare orangedemo package to contain widgets for the "Demo" category
      entry_points={"orange.widgets": "UNComtrade = my_code.Orange_widget.orange_widget"},

      install_requires=[
        'requests',
        'Orange3',
        'numpy',
      ],

      author="Marko Zeman",
)