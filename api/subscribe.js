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

  const { email, utm_source, utm_medium, utm_campaign, referrer } = req.body || {};

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ error: 'Invalid email' });
  }

  const { error } = await supabase.from('subscribers').upsert(
    {
      email: email.toLowerCase().trim(),
      utm_source: utm_source || 'direct',
      utm_medium: utm_medium || null,
      utm_campaign: utm_campaign || null,
      referrer: referrer || null,
    },
    { onConflict: 'email', ignoreDuplicates: true }
  );

  if (error) {
    console.error('subscribe error:', error);
    return res.status(500).json({ error: 'Failed to save' });
  }

  return res.status(200).json({ success: true });
};
