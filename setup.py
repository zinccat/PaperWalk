from setuptools import setup, find_packages

setup(
    name='PaperWalk',
    version='0.1.0',
    author='ZincCat',
    author_email='zincchloride@outlook.com',
    description='A package for random walking on the paper citation network.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/zinccat/PaperWalk',
    package_dir={'': 'src'},  # Specify that packages are under src
    packages=find_packages(where='src'),  # Tell setuptools to find packages under src
    install_requires=[
        'neo4j'
        # Add other dependencies as needed
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.8',
)