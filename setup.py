from setuptools import setup, find_packages


setup(
    name="UNComtrade",
    description="Widget which extracts data from UN Comtrade API and makes possible to operate on this data.",

    packages=["orangecontrib", "orangecontrib.uncomtrade", "orangecontrib.uncomtrade.widget"],
    # packages=find_packages(),
    package_data={"widget": ["icons/*.svg", "icons/*.jpg"],
                  "uncomtrade": ["data/*.json"]},
    include_package_data=True,

    classifiers=[
        'Programming Language :: Python',
        'Operating System :: OS Independent'
    ],

    entry_points={
        "orange.widgets": "UNComtrade = orangecontrib.uncomtrade.widget"
    },

    install_requires=[
        'requests',
        'Orange3',
        'numpy',
    ],

    author="Marko Zeman",
    author_email="marko.zeman@gmail.com",
)