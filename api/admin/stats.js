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
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Admin-Token');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (!checkAuth(req)) return res.status(401).json({ error: 'Unauthorized' });

  const [{ data: clicks }, { data: subscribers }] = await Promise.all([
    supabase.from('clicks').select('article_id, utm_source, created_at'),
    supabase.from('subscribers').select('utm_source, created_at'),
  ]);

  const clicksByArticle = {};
  const clicksBySource = {};
  (clicks || []).forEach(c => {
    clicksByArticle[c.article_id] = (clicksByArticle[c.article_id] || 0) + 1;
    const src = c.utm_source || 'direct';
    clicksBySource[src] = (clicksBySource[src] || 0) + 1;
  });

  const subsBySource = {};
  const subsByDay = {};
  (subscribers || []).forEach(s => {
    const src = s.utm_source || 'direct';
    subsBySource[src] = (subsBySource[src] || 0) + 1;
    const day = s.created_at?.split('T')[0];
    if (day) subsByDay[day] = (subsByDay[day] || 0) + 1;
  });

  return res.status(200).json({
    total_subscribers: (subscribers || []).length,
    total_clicks: (clicks || []).length,
    clicks_by_article: clicksByArticle,
    clicks_by_source: clicksBySource,
    subs_by_source: subsBySource,
    subs_by_day: subsByDay,
  });
};
