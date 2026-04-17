-- ============================================================
-- Pre-IPO Outpost — Supabase Schema
-- 在 Supabase 控制台 > SQL Editor 中粘贴并执行
-- ============================================================

-- 1. 订阅者表
CREATE TABLE IF NOT EXISTS subscribers (
  id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  email       text UNIQUE NOT NULL,
  utm_source  text,
  utm_medium  text,
  utm_campaign text,
  referrer    text,
  created_at  timestamptz DEFAULT now()
);

-- 2. 点击埋点表
CREATE TABLE IF NOT EXISTS clicks (
  id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  article_id  text NOT NULL,
  event       text DEFAULT 'click',
  utm_source  text,
  session_id  text,
  created_at  timestamptz DEFAULT now()
);

-- 3. 文章配置表
CREATE TABLE IF NOT EXISTS articles (
  id            text PRIMARY KEY,
  title         text NOT NULL,
  description   text,
  url           text DEFAULT '',
  category_tag  text DEFAULT '基础普及',
  is_free       boolean DEFAULT false,
  updated_at    timestamptz DEFAULT now()
);

-- ============================================================
-- Row Level Security
-- ============================================================

ALTER TABLE subscribers ENABLE ROW LEVEL SECURITY;
ALTER TABLE clicks      ENABLE ROW LEVEL SECURITY;
ALTER TABLE articles    ENABLE ROW LEVEL SECURITY;

-- 前端可以写入（匿名用户提交邮箱/埋点）
CREATE POLICY "anon_insert_subscribers" ON subscribers
  FOR INSERT TO anon WITH CHECK (true);

CREATE POLICY "anon_insert_clicks" ON clicks
  FOR INSERT TO anon WITH CHECK (true);

-- 前端可以读文章配置
CREATE POLICY "anon_read_articles" ON articles
  FOR SELECT TO anon USING (true);

-- 后端 service_role 全权访问
CREATE POLICY "service_role_subscribers" ON subscribers
  FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "service_role_clicks" ON clicks
  FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "service_role_articles" ON articles
  FOR ALL TO service_role USING (true) WITH CHECK (true);

-- ============================================================
-- 初始文章数据（10篇，URL 后台填写）
-- ============================================================

INSERT INTO articles (id, title, description, url, category_tag, is_free) VALUES
('01', 'SpaceX IPO 倒计时：1.75 万亿估值背后的时间线与投资机会全解析',
 '一文帮你梳理史上最大 IPO 的关键节点、承销商阵容以及散户入场的现实障碍。',
 '', '基础普及', true),

('02', '不用等 IPO 配售：4 种"成份股"策略让你提前布局 SpaceX 生态',
 'DXYZ、XOVR、ARKX、SATS... 深度对比 4 种能让你间接持有 SpaceX 的代理资产。',
 '', '核心方法论', true),

('03', '深度拆解：每一只 SpaceX 概念标的的真实风险',
 '主动排雷：有标的溢价高达 40%，有标的被出具"持续经营疑虑"，你的钱可能去了哪里？',
 '', '风险评测', true),

('04', '手把手实操教程：如何用 USDT 一键买入 SpaceX 概念标的',
 '在 OpenBIT App 内的具体操作指引，限价单/市价单使用技巧及手续费优化方案。',
 '', '实操教程', false),

('05', '$500 / $5K / $50K 的 SpaceX 生态梯队建仓方案',
 '不同资金体量的风险偏好对应指南，组合搭配实现胜率最大化。',
 '', '资金管理', false),

('06', 'IPO 当天如何操作：申购、定价与上市首日策略',
 '从 T-3 到上市首日，每个关键时间点你应该做什么、避开什么。',
 '', '实战策略', false),

('07', 'SpaceX 核心财务拆解：营收、利润率与成长空间',
 'S-1 公开后第一时间解读：Starlink 真实 ARPU、发射业务壁垒与成长天花板。',
 '', '财务分析', false),

('08', '风险对冲指南：如果 IPO 推迟或市场暴跌怎么办',
 '多空配置、止损逻辑与极端情景下的具体应对方案。',
 '', '风险管理', false),

('09', '历史复盘：从 Uber 到 Airbnb，Pre-IPO 标的的规律',
 '分析 5 个超级 IPO 的前哨布局收益数据，找出可复制的规律。',
 '', '历史复盘', false),

('10', '此刻的操作建议：基于当前市场数据的具体仓位建议',
 '结合当前 DXYZ 溢价率、市场情绪指数，给出具体建仓时机与仓位比例。',
 '', '实时策略', false)
ON CONFLICT (id) DO NOTHING;
