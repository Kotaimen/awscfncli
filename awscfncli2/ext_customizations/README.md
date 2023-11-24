## External CloudFormation AWS CLI Dependencies

The code in this dirctory is directly copied from: https://github.com/aws/aws-cli/tree/v2/awscli/customizations/cloudformation

Previous to this the codebase brought int the awscli package as a dependency, however that brings in issues with AWS CLI v2 and the move away from PpPi

These issues are:

1. AWS CLI v2 isnt on PyPi - hence for CLI v2 you need a dependency based on a git link which isnt allowed  - https://discuss.python.org/t/packages-installed-from-pypi-cannot-depend-on-packages-which-are-not-also-hosted-on-pypi/3736
2. AWS CLI v1 dependency would mean two versions of AWS CLI installed on a given machine
3. AWS CLI v1 development has effectively stopped and continuing to install it as a dependency is counter to the aims of its depreciation.

Therefore we just include the small amount of files directly and avoid any hard dependency. These files are updated very infrequently and will be synced manually across releases.