const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).end();

  const { article_id, event, utm_source, session_id } = req.body || {};

  const { error } = await supabase.from('clicks').insert({
    article_id: article_id || 'unknown',
    event: event || 'click',
    utm_source: utm_source || 'direct',
    session_id: session_id || null,
  });

  if (error) console.error('track error:', error);
  return res.status(200).json({ success: true });
};
