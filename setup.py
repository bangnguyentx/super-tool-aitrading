from setuptools import setup, find_packages

setup(
    name="trading-signals-website",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "flask==2.3.3",
        "pandas==1.5.3", 
        "numpy==1.24.3",
        "requests==2.31.0",
        "apscheduler==3.10.1",
        "ta==0.10.2",
        "gunicorn==21.2.0",
        "cryptography==41.0.7"
    ],
)
