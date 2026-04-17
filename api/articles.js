const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 'public, max-age=300');
  if (req.method !== 'GET') return res.status(405).end();

  const { data, error } = await supabase
    .from('articles')
    .select('*')
    .order('id');

  if (error) return res.status(500).json({ error: 'Failed to fetch' });
  return res.status(200).json(data);
};
