from setuptools import setup

setup(name="UNComtrade",
      packages=["orange_widget"],
      package_data={"orange_widget": ["icons/*.svg", "icons/*.jpg"]},
      classifiers=["Example :: Invalid"],
      # Declare orangedemo package to contain widgets for the "Demo" category
      entry_points={"orange.widgets": "UNComtrade = orange_widget"},

      install_requires=[
        'requests',
        'Orange3',
        'numpy',
      ],

      author="Marko Zeman",
)