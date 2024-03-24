import os
from setuptools import setup

directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(directory, 'README.md'), encoding='utf-8') as f:
  long_description = f.read()

setup(name='python-jsonllm',
      version='0.0.3.1',
      description='LLM please cast to JSON',
      author='Ivan Belenky',
      license='MIT',
      url = 'https://github.com/ivanbelenky/jsonllm',
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages = ['jsonllm'],
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
      ],
      install_requires=[
        'retry==0.9.2', 
        'vertexai==1.43.0', 
        'openai==1.14.2', 
        'google-cloud-aiplatform==1.44.0', 
        'tiktoken==0.6.0', 
        'anthropic==0.21.3',
        'python-dotenv==1.0.1'
      ],
      python_requires='>=3.8',
      include_package_data=True)
