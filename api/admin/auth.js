module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).end();

  const { password } = req.body || {};

  if (password && password === process.env.ADMIN_PASSWORD) {
    const token = Buffer.from(`${password}:${process.env.ADMIN_PASSWORD}`).toString('base64');
    return res.status(200).json({ success: true, token });
  }

  return res.status(401).json({ error: 'Incorrect password' });
};
