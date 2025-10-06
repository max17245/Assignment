const express = require('express');
const axios = require('axios');
const _ = require('lodash');
const minimist = require('minimist');
const moment = require('moment');
const qs = require('qs');
const debug = require('debug')('demo');

const app = express();
const argv = minimist(process.argv.slice(2));
const PORT = argv.port || process.env.PORT || 3000;

app.get('/', async (req, res) => {
  // แค่เดโม: เรียก public API และรวมข้อมูลแบบเรียบง่าย
  try {
    const params = { t: moment().toISOString() };
    const url = 'https://httpbin.org/get?' + qs.stringify(params);
    const { data } = await axios.get(url);

    const picked = _.pick(data, ['args', 'headers', 'origin', 'url']);
    debug('Fetched data keys:', Object.keys(picked));

    res.json({
      ok: true,
      message: 'SCA/SBOM demo running',
      time: moment().format(),
      sample: picked
    });
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});

app.listen(PORT, () => {
  console.log(`Demo running on http://localhost:${PORT}`);
});
