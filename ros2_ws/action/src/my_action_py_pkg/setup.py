from setuptools import find_packages, setup

package_name = 'my_action_py_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='b4643',
    maintainer_email='b46435298@google.com',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'action_server = my_action_py_pkg.countdown_server:main',
            'action_client = my_action_py_pkg.countdown_client:main',
        ],
    },
)
