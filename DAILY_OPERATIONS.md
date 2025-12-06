# 📅 A Day in the Life of Your AI Solopreneur Bot

Now that your bot is **LIVE**, here is exactly what it does every single day, automatically.

---

## 🌅 Morning Strategy (06:00 UTC)

**The "Brain" Wakes Up**
Before writing a single tweet, the bot acts like a strategist.
1.  **Scans the Web**: It visits Reddit, Hacker News, GitHub, and Google Trends.
2.  **Identifies Trends**: It looks for rising topics in your niches (AI, Automation, Solopreneurship).
3.  **Create a Plan**: It writes a strategy document (`data/trend_plans/TREND_PLAN_YYYY_MM_DD.md`) deciding:
    *   *What are people talking about today?*
    *   *What angle should we take?*

---

## 🏭 Content Factory (Runs Every 6 Hours)
*(07:00, 13:00, 19:00, 01:00 UTC)*

**The "Writer" Gets to Work**
Using the morning's plan, the bot generates content batches.
1.  **Selects a Topic**: e.g., "AI Agents for Lead Gen".
2.  **Drafts Content**: Uses OpenAI (GPT-3.5) to write:
    *   **Tweets**: Punchy, viral-style hooks.
    *   **Threads**: Educational step-by-step guides.
    *   **CTAs**: Soft sells for your digital products.
3.  **Quality Check**: It formats the text, adds hashtags, and ensures it fits the character limit.
4.  **Queues It**: Adds the best items to `data/content_queue.json`.

---

## 📢 Publishing Schedule (Your Tweets)
*(Times are approximate based on `config/twitter_settings.yaml`)*

The bot automatically picks the best content from the queue and posts it at high-engagement times.

| Time (UTC) | Content Type | Purpose |
| :--- | :--- | :--- |
| **09:00 AM** | 🧵 **Thread** | **Value/Education**: Deep dive into a topic to build authority. |
| **12:00 PM** | 🐦 **Tweet** | **Engagement**: A contrarian take or quick tip. |
| **03:00 PM** | 🐦 **Tweet** | **Growth**: Trending news or insight. |
| **06:00 PM** | 📣 **CTA/Tweet** | **Sales**: Promoting your product or newsletter. |

*You don't need to do anything. The bot handles the posting API calls.*

---

## 🧠 Nightly Analysis (00:00 Midnight UTC)

**The "Analyst" Reviews Performance**
1.  **Checks Stats**: Looks at the last 24 hours of posts.
    *   *Which tweets got likes?*
    *   *which links were clicked?*
2.  **Updates Scores**: It gives "points" to topics that performed well.
3.  **Learns**: Topics with high scores are *more likely* to be picked again tomorrow.

---

## 🛡️ Safety Systems (Always On)

-   **Circuit Breaker**: If OpenAI isn't responding, the bot switches to "Safe Mode" (using templates) so it never misses a post.
-   **Rate Limiter**: It strictly follows Twitter's limits (max 17 tweets/day) to keep your account safe.
-   **Logs**: Every action is recorded in `data/logs/` so you can verify what happened.

---

## 👤 Your Role (Optional)

You can mostly ignore it! But if you want to intervene:
1.  **Check the Plan**: Read `data/trend_plans/` to see what it's thinking.
2.  **Manual Override**: You can edit `data/content_queue.json` if you want to change a specific scheduled post.
3.  **Monitor**: Watch the [GitHub Actions page](https://github.com/Feroz723/autonomous_ai/actions) to see green checkmarks ✅.

**Summary**: You now have a full-time social media manager working 24/7 for free.
