from setuptools import setup

setup(name="Demo",
      packages=["orange_widget"],
      package_data={"orange_widget": ["icons/*.svg"]},
      classifiers=["Example :: Invalid"],
      # Declare orangedemo package to contain widgets for the "Demo" category
      entry_points={"orange.widgets": "Demo = orange_widget"},
      )