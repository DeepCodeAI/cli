import re

GIT_URI_OBJ = re.compile('((git@|https://)(?P<platform>[\w\.@]+)(/|:))(?P<owner>[\w,\-,\_]+)/(?P<repo>[\w,\-,\_]+)(.git){0,1}((/){0,1})((@(?P<oid>[0-9]+)){0,1})', re.IGNORECASE)

def parse_git_uri(uri):
    """
    Parses git uri into dictionary. Both SSH and HTTPS versions are supported
    SSH version git@github.com:DeepCodeAI/cli.git@1234
    HTTPS version https://github.com/DeepCodeAI/cli.git@1234
    
    In both cases the result should be: \{ platform: gh, owner: DeepCodeAI, repo: cli, oid: 1234 \}
    """
    match = GIT_URI_OBJ.match(uri)
    if match:
        return match.groupdict()
