const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

function checkAuth(req) {
  const token = req.headers['x-admin-token'];
  if (!token) return false;
  try {
    const decoded = Buffer.from(token, 'base64').toString();
    const [pw] = decoded.split(':');
    return pw === process.env.ADMIN_PASSWORD;
  } catch { return false; }
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, PUT, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Admin-Token');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (!checkAuth(req)) return res.status(401).json({ error: 'Unauthorized' });

  if (req.method === 'GET') {
    const { data, error } = await supabase.from('articles').select('*').order('id');
    if (error) return res.status(500).json({ error: 'Failed to fetch' });
    return res.status(200).json(data);
  }

  if (req.method === 'PUT') {
    const { id, title, description, url, category_tag, is_free } = req.body || {};
    if (!id) return res.status(400).json({ error: 'Missing id' });

    const { error } = await supabase.from('articles').upsert({
      id,
      title,
      description,
      url: url || '',
      category_tag,
      is_free: Boolean(is_free),
      updated_at: new Date().toISOString(),
    });

    if (error) return res.status(500).json({ error: 'Failed to update' });
    return res.status(200).json({ success: true });
  }

  return res.status(405).end();
};
