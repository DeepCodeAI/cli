# A list of commonly ignored directories

#  Bash command to produce this list:
#
#  git clone https://github.com/toptal/gitignore &&
#  cd gitignore/templates &&
#  cat * |
#  Only keep directories
#  grep '/$' |
#  Remove comments and negated rules
#  grep '^[^!#]' |
#  Remove specific rules
#  grep -v '^*/$' |
#  grep -v 'src/' |
#  Remove duplicates
#  sort | uniq |
# Make an array out of it
#  awk '{print "\""$0"\","} END{print "]"} BEGIN{print "["}'

COMMON_IGNORE_DIRS = [
    "[Aa][Rr][Mm]/",
    "[Aa][Rr][Mm]64/",
    "[Aa]ssets/TextMesh*Pro/",
    ".ab/",
    ".accio/",
    "admin-dev/autoupgrade/",
    "admin-dev/backups/",
    "admin-dev/export/",
    "admin-dev/import/",
    ".alpackages/",
    "**/android/captures/",
    "/.anjuta/",
    "*.app/",
    "**/App_Data/cache/",
    "**/App_Data/Logs/",
    "**/App_Data/NuGetBackup/",
    "**/App_Data/[Pp]review/",
    "**/App_Data/TEMP/",
    "appengine-generated/",
    "/Application/Runtime/",
    "AppPackages/",
    "app/storage/",
    ".apt_generated/",
    "archive/",
    "arm/",
    "arm-p/",
    "artifacts/",
    "ASALocalRun/",
    "assets/",
    "assets/_combinedfiles/",
    "assets/_resampled/",
    "assets/Uploads/",
    "/AS/System/",
    "AudioCache/",
    "/auto/",
    "AutoTest.Net/",
    "backup/",
    "Backup*/",
    "[Bb]in/",
    "/[Bb]uild/",
    "[Bb]uild/",
    "/[Bb]uilds/",
    "*/*/*/bd/*/ip/*/*/",
    "*/*/bd/*/ip/*/*/",
    "BenchmarkDotNet.Artifacts/",
    "/bin/",
    "bin/",
    "binaries/",
    "/Binaries/",
    "bin-debug/",
    "bin-release/",
    "/bitrix/",
    "bld/",
    "/blib/",
    ".bloop/",
    "bom/",
    "_Boot/",
    "bower_components/",
    ".buckd/",
    "buck-out/",
    "_build/",
    "/.build/",
    "/*/build/",
    "/build/",
    ".build/",
    "**/build/",
    "build-*/",
    "build/",
    "build/build/",
    "build-iPhoneOS/",
    "build-iPhoneSimulator/",
    "build_isolated/",
    "/build_local/",
    "_build.prev/",
    "/build_production/",
    "Builds/",
    "/build_staging/",
    "build_*_vc10/",
    "build_*_xcode/",
    "/.bundle/",
    "BundleArtifacts/",
    ".bzr/",
    ".cabal-sandbox/",
    "/cache/",
    ".cache/",
    "*_cache/",
    "*-cache/",
    "cache/",
    "captures/",
    ".cask/",
    "/cfg/cpp/",
    "/checkouts/",
    "**/*.chk/",
    "/classes/",
    "classes/",
    "Clean System Files/",
    "ClientBin/",
    "/_clouddata/",
    ".cm/",
    "cmake-build-*/",
    "cocos/scripting/lua-bindings/proj.ios_mac/build/",
    "codegen/",
    "compiled/",
    "Compiled/",
    "_CompileInfo/",
    "/composer/modules/web/dist-electron/",
    ".config/",
    "config/",
    "/config/development/",
    "configs/",
    ".consulo/",
    "contents/",
    "cookbooks/",
    ".coq-native/",
    "cov*/",
    "/coverage/",
    "cover_db/",
    ".cpcache/",
    ".cr/",
    "**/.crdb/",
    "csx/",
    "/custom/application/Ext/",
    "custom_components/",
    "/custom/history/",
    "/custom/modulebuilder/",
    "/custom/modules/*/Ext/",
    "/custom/working/",
    ".dart_tool/",
    ".data/",
    "*-data/",
    "data/cache/",
    "data/DoctrineORMModule/cache/",
    "data/DoctrineORMModule/Proxy/",
    "data/logs/",
    "data/sessions/",
    "data/tmp/",
    "[Dd]ebug/",
    "[Dd]ebug*/",
    "[Dd]ebugPS/",
    "[Dd]ebugPublic/",
    "[Dd]ebug.win32/",
    "/debug/",
    "_Debug/",
    "Debug/",
    "**/Debug/Exe/",
    "/defaults/",
    "demos/",
    "dependencies/",
    "Dependencies/",
    "deploy/",
    ".deploy_git/",
    "deps/downloads/",
    "deps/usr/",
    "DerivedData/",
    "devel/",
    "devel_isolated/",
    "develop-eggs/",
    "Device-Debug/",
    "Device-Release/",
    "dev/pr-deps/",
    "**/.df_cache/",
    "/Diagnosis/",
    "disassembly/",
    "/dist/",
    "dist/",
    ".divinercache/",
    "/doc/",
    "**/doc/api/",
    "doc/api/",
    "docgen_tmp/",
    "_docpress/",
    "DocProject/buildhelp/",
    "/docs/",
    "docs/",
    "docs/_build/",
    "docs/build/",
    "docs/site/",
    "download/",
    "downloads/",
    "**/*dsgn.autobk/",
    "**/*.dsgn.prm/",
    "*.dSYM/",
    "DVEfiles/",
    ".dynamodb/",
    "ecf/",
    "[Ee]xpress/",
    "*.egg-info/",
    ".eggs/",
    "eggs/",
    ".elasticbeanstalk/",
    ".elixir_ls/",
    "/elpa/",
    "**/*.emc/",
    ".ensime_cache/",
    ".ensime_lucene/",
    "env/",
    "ENV/",
    "env.bak/",
    "escue-backup/",
    "_esy/",
    "/_eumm/",
    "/exploded-archives/",
    "export/",
    "Export/",
    "ExportedObj/",
    "ext/",
    "ext/build/",
    ".externalToolBuilders/",
    "ext/modules/",
    ".exvim.*/",
    ".fake/",
    "fake-eggs/",
    "FakesAssemblies/",
    "/fileadmin/_processed_/",
    "/fileadmin/_temp_/",
    "/fileadmin/user_upload/",
    "/*_files/",
    "files/",
    "/files/documents/",
    "/files/downloads/",
    ".firebase/",
    "Flash/",
    "freeline/",
    ".fusebox/",
    "gen/",
    "generated/",
    "Generated_Code/",
    "Generated\ Files/",
    ".generated-tests/",
    "generated-tests/",
    "/Godeps/",
    ".gradle/",
    ".gwt/",
    ".gwt-tmp/",
    "gwt-unitCache/",
    "hadoop-common-project/hadoop-kms/downloads/",
    "helpsearch*/",
    ".hg/",
    "__history/",
    "hooks/",
    ".HTF/",
    "html/",
    "htmlcov/",
    ".hypothesis/",
    "icloud/",
    ".idea/",
    ".idea/caches/",
    ".idea/**/dataSources/",
    ".idea/libraries/",
    ".idea_modules/",
    ".idea/shelf/",
    "image/cache/",
    "image/data/",
    "images/avatars/",
    "images/captchas/",
    "images/member_photos/",
    "images/pm_attachments/",
    "images/signature_attachments/",
    "images/smileys/",
    ".import/",
    "inc/",
    "**/IntegrationServer/datastore/",
    "**/IntegrationServer/db/",
    "**/IntegrationServer/DocumentStore/",
    "**/IntegrationServer/lib/",
    "**/IntegrationServer/logs/",
    "**/IntegrationServer/packages/Wm*/",
    "**/IntegrationServer/replicate/",
    "**/IntegrationServer/sdk/",
    "**/IntegrationServer/support/",
    "**/IntegrationServer/update/",
    "**/IntegrationServer/userFtpRoot/",
    "**/IntegrationServer/web/",
    "**/IntegrationServer/WmRepository4/",
    "**/IntegrationServer/XAStore/",
    "**/ios/**/DerivedData/",
    "**/ios/Flutter/flutter_assets/",
    "**/ios/.generated/",
    "iOSInjectionProject/",
    "**/ios/**/Pods/",
    "**/ios/**/.symlinks/",
    "**/ios/**/*sync/",
    "**/ios/**/.vagrant/",
    "ipch/",
    "iseconfig/",
    "javadoc/",
    ".jekyll-cache/",
    "jgiven-reports/",
    "jsb/",
    "jsb-binary/",
    "jsb-default/",
    "jsb-link/",
    "jspm_packages/",
    ".kdev4/",
    ".kitchen/",
    "kobaltBuild/",
    "latex.out/",
    ".launches/",
    ".lein-plugins/",
    ".lgt_tmp/",
    "lgt_tmp/",
    "/lib/",
    ".lib/",
    "lib/",
    "lib64/",
    "/lib/bundler/man/",
    "lib_managed/",
    "_Libraries/",
    "library/",
    ".libs/",
    "libs/",
    "/.link_to_grails_plugins/",
    "lint/generated/",
    "lint/intermediates/",
    "lint/outputs/",
    "lint/tmp/",
    "/[Ll]ibrary/",
    "[Ll]og/",
    "/[Ll]ogs/",
    "local/",
    "locales/",
    ".localhistory/",
    "log/",
    "/logs/",
    "logs/",
    "logtalk_doclet_logs/",
    "logtalk_tester_logs/",
    "manifest/cache/",
    "manifest/logs/",
    "manifest/tmp/",
    "/media/archive/",
    "/media/image/",
    "/media/music/",
    "/media/pdf/",
    "/media/temp/",
    "/media/unknown/",
    "/media/video/",
    "Mercury/",
    ".metals/",
    "metastore/",
    "metastore_db/",
    ".mfractor/",
    "MigrationBackup/",
    "/[Mm]emoryCaptures/",
    "modules/",
    ".mono/",
    "msg_gen/",
    ".mtj.tmp/",
    ".mypy_cache/",
    ".navigation/",
    "nbbuild/",
    "nbdist/",
    ".nb-gradle/",
    "**/nbproject/private/",
    "nbproject/private/",
    "_ngo/",
    "nimcache/",
    "/node_modules/",
    "node_modules/",
    ".nox/",
    "obj/",
    "/old/",
    "/[Oo]bj/",
    "[Oo]bj/",
    "_opam/",
    "OpenCover/",
    ".otto/",
    "/out/",
    "out/",
    "output/",
    "Package Control.ca-certs/",
    "Package Control.cache/",
    "packer_cache/",
    "paket-files/",
    "/parts/",
    "parts/",
    "/Physical/*/*/*/DLFiles/",
    "pip-wheel-metadata/",
    "/pkg/",
    "pkg/",
    "platforms/",
    "plugins/",
    "pnacl/",
    "Pods/",
    "/prebuilt/",
    "*-prefix/",
    "Prerequisites/",
    "**/__Previews/",
    "/prime/",
    "prime/",
    "/priv/static/",
    "profile_default/",
    "proguard/",
    ".project/",
    "project/boot/",
    "project/build/target/",
    "Project\ Logs*/",
    "Project\ Outputs*/",
    "project/plugins/lib_managed/",
    "project/plugins/project/",
    "project/plugins/src_managed/",
    "project/plugins/target/",
    "projects/",
    "_protected/app/system/core/assets/cron/_delay/",
    "_protected/data/tmp/",
    ".pub/",
    ".pub-cache/",
    "/public/",
    "public/",
    "public/resources/",
    "publish/",
    "PublishScripts/",
    "pvsbin/",
    "__pycache__/",
    ".pyre/",
    ".pytest_cache/",
    "pythontex-files-*/",
    "/QuickLook/",
    "quick-test/runnable/",
    "RAM/",
    "rcf/",
    "/*.Rcheck/",
    "/rdoc/",
    ".recommenders/",
    "__recovery/",
    "$RECYCLE.BIN/",
    "release/",
    "Release/",
    "reports/",
    "rerun/",
    "_ReSharper*/",
    "resources/",
    "resources/customlibs/lib/android/",
    "resources/customlibs/lib/ipad/",
    "resources/customlibs/lib/iphone/",
    "resources/customlibs/lib/tabrcandroid/",
    "resources/customlibs/lib/windows10/",
    "resources/customlibs/lib/winphone10/",
    "/resources/_gen/",
    "resources/i18n/",
    "resources/sass/.sass-cache/",
    "rpc/",
    ".Rproj.user/",
    "[Rr]elease/",
    "[Rr]elease*/",
    "[Rr]eleasePS/",
    "[Rr]eleases/",
    "[Rr]elease.win32/",
    "run/",
    "runtime/",
    "*-sapl/",
    ".sass-cache/",
    ".scannerwork/",
    "sccprj/",
    "screenshots/",
    "sdist/",
    "/server/",
    ".serverless/",
    "ServiceFabricBackup/",
    ".settings/",
    "settings/",
    "*-SetupFiles/",
    "/.shards/",
    "share/python-wheels/",
    "**/*.si/",
    ".signing/",
    "silverstripe-cache/",
    "Simulator/",
    ".Simulator-Debug/",
    "simv.daidir/",
    "simv.db.dir/",
    "simv.vdb/",
    "_site/",
    "/**/_site/",
    "sites/site*/admin/",
    "sites/site*/private/",
    "sites/site*/public/admin/",
    "sites/site*/public/setup/",
    "sites/site*/public/theme/",
    "sized/",
    "slprj/",
    "/snap/.snapcraft/",
    "/.sonar/",
    ".sonar/",
    ".sonarlint/",
    ".sourcemaps/",
    "spark-warehouse/",
    "/spec/reports/",
    "src-gen/",
    "src_managed/",
    "srv_gen/",
    ".stack-work/",
    "/stage/",
    "stage/",
    ".sts4-cache/",
    ".svn/",
    "symphony/",
    "sympy-plots-for-*.tex/",
    "system/cache/",
    "system/logs/",
    "system/storage/",
    "system/tests/source/units/auto-tests/",
    "/target/",
    "target/",
    ".Target-Debug/",
    "/target-eclipse/",
    ".Target-Release/",
    ".temp/",
    "temp/",
    "/Temp/",
    "templates/",
    "/templates/*-template-binary/",
    "TempStatsStore/",
    "/test-build/",
    "testit-reports/",
    "/test-output/",
    "/test-report/",
    "test-results/",
    "test-servers/",
    "/tests/js-tests/res/",
    "tests/*/publish/",
    "tests/*/runtime/",
    "/tests/Shopware/TempFiles/",
    "tests/source/units/auto-tests/",
    "/test/tmp/",
    "/test/version_tmp/",
    "textpattern/",
    "$tf/",
    "themes/*/cache/",
    "themes/classic/views/",
    "themes/simple/",
    "_thumbs/",
    "thumbs/",
    "/tmp/",
    ".tmp/",
    "tmp/",
    "tmp/nanoc/",
    ".tmp_versions/",
    "/tools/fbx-conv/",
    "/tools/framework-compile/bin/proj_modifier/plutil-win32/",
    ".tox/",
    "/[Tt]emp/",
    "[Tt]est[Rr]esult*/",
    "typings/",
    "/typo3temp/",
    "_UpgradeReport_Files/",
    "/Upgrades/",
    "/upload/",
    "upload/",
    "/upload_backup/",
    "/uploads/",
    "urgReport/",
    ".vagrant/",
    "var/",
    "/vendor/",
    "vendor/",
    "venv/",
    "venv.bak/",
    ".vimfiles.*/",
    ".vs/",
    ".vscode/",
    ".waf-*-*/",
    "waf-*-*/",
    ".waf3-*-*/",
    "waf3-*-*/",
    "warehouse/",
    "war/gwt_bree/",
    "war/WEB-INF/classes/",
    "war/WEB-INF/deploy/",
    "/web/bundles/",
    "/web/css/",
    "web-desktop/",
    "/web/fileadmin/",
    "/web/js/",
    "web-mobile/",
    "/web/typo3conf/ext/",
    "/web/typo3conf/l10n/",
    "/web/uploads/",
    "/web/var/",
    "wheels/",
    "work/",
    "workspace/uploads/",
    "wp-content/themes/twenty*/",
    "*-www/",
    "www/",
    "www-test/",
    "x64/",
    "x86/",
    "xcuserdata/",
    "xlnx_auto_0_xdb/",
    "_xmsgs/",
    "xst/",
    "xtend-gen/",
    "/_yardoc/",
    "/.yardoc/",
    "zig-cache/",
]
