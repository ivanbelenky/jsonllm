import os
from setuptools import setup

directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(directory, 'README.md'), encoding='utf-8') as f:
  long_description = f.read()

setup(name='python-jsonllm',
      version='0.0.2',
      description='LLM please cast to JSON',
      author='Ivan Belenky',
      license='MIT',
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages = ['jsonllm'],
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
      ],
      install_requires=['retry', 'vertexai', 'openai', 'google-cloud-aiplatform', 'tiktoken', 'anthropic', 'python-dotenv'],
      python_requires='>=3.8',
      include_package_data=True)
