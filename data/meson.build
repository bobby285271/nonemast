# SPDX-FileCopyrightText: 2022 Jan Tojnar
# SPDX-License-Identifier: MIT

appstream_file = i18n.merge_file(
  input: f'@application_id@.appdata.xml.in',
  output: f'@application_id@.appdata.xml',
  po_dir: '../po',
  install: true,
  install_dir: nonemast_datadir / 'appdata',
)

appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test(
    'Validate appstream file',
    appstream_util,
    args: [
      'validate',
      appstream_file,
    ],
  )
endif

install_data(
  'cz.ogion.Nonemast.gschema.xml',
  install_dir: get_option('datadir') / 'glib-2.0' / 'schemas'
)

subdir('icons')
