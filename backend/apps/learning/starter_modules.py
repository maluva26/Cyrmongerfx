"""Default Forex learning modules shared with every account."""


STARTER_MODULES = (
    {
        "key": "forex-introduction",
        "title": "Module 1: Introduction to Forex & Currency Pairs",
        "category": "Forex Foundations",
        "summary": "Understand currency quotes, pair types, liquidity, and global trading sessions.",
        "order_index": 10,
        "image_url": "/learning-images/currency-pairs.jpg",
        "image_alt": "A close-up of US dollar banknotes representing currency exchange.",
        "body": """
<h2>What is Forex?</h2>
<p>Foreign exchange (Forex or FX) is the market in which one currency is exchanged for another. A quoted exchange rate expresses the price of one currency in units of another. The retail market is largely over the counter, so prices, costs, and protections can differ between providers.</p>
<h2>How currency pairs work</h2>
<p>In EUR/USD, EUR is the base currency and USD is the quote currency. A quote of 1.0850 means one euro is priced at 1.0850 US dollars. Buying the pair means buying the base currency and selling the quote currency; selling the pair does the reverse. A rising pair means the base currency has strengthened relative to the quote currency, before costs.</p>
<h2>Major, minor, and exotic pairs</h2>
<p>Market conventions often call heavily traded pairs that include USD majors. Crosses (sometimes called minors) do not include USD, such as EUR/GBP. Exotic pairs combine a major currency with a less frequently traded currency. Liquidity and spreads vary by provider and market conditions; a label does not guarantee a low cost or a suitable trade.</p>
<h2>Market hours and sessions</h2>
<p>Spot FX trading generally follows a near 24-hour, five-day cycle as business hours move through regional financial centres, including Sydney, Tokyo and other Asian centres, London, and New York. Session times overlap and shift with daylight-saving changes. Activity can rise during overlaps, but volatility and liquidity are not guaranteed.</p>
<p><strong>Learning note:</strong> Forex involves substantial risk. This material explains market terms; it is not a recommendation to trade.</p>
<h2>Further reading</h2>
<ul><li><a href="https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/foreign">Investor.gov: Foreign Currency Exchange (Forex) Trading</a></li><li><a href="https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/CustomerAdvisory_MustKnowForex.html">CFTC: Eight Things to Know Before Trading Forex</a></li></ul>
""",
        "questions": (
            ("What does a Forex exchange rate describe?", "The price of one currency expressed in another currency.", ("The guaranteed profit from a trade.", "The fee charged to open a bank account.", "The number of shares in a company."), "An exchange rate is the relative price of two currencies; it does not predict a guaranteed return."),
            ("In EUR/USD, which currency is the base currency?", "EUR, the first currency in the pair.", ("USD, the second currency in the pair.", "Both currencies are always base currencies.", "The currency with the higher exchange rate."), "The first currency in a standard pair quote is the base currency."),
            ("If EUR/USD is quoted at 1.0850, what does that quote mean?", "One euro is priced at 1.0850 US dollars.", ("One US dollar is priced at 1.0850 euros.", "One euro costs 1.0850 British pounds.", "The euro will rise by 1.0850 percent."), "The quote gives the number of quote-currency units (USD) for one base-currency unit (EUR)."),
            ("What does buying EUR/USD represent in pair terms?", "Buying EUR and selling USD.", ("Selling EUR and buying USD.", "Buying both EUR and USD.", "Buying a share in the European Central Bank."), "A long position in a pair buys its base currency and sells its quote currency."),
            ("Which is an example of a currency cross that does not include USD?", "EUR/GBP.", ("EUR/USD.", "USD/JPY.", "GBP/USD."), "EUR/GBP pairs the euro with the pound and does not contain USD."),
            ("What is commonly meant by an exotic currency pair?", "A major currency paired with a less frequently traded currency.", ("A pair traded only on weekends.", "A pair that cannot change price.", "Any pair that contains USD."), "The term generally refers to a major currency matched with a less frequently traded currency; definitions can vary."),
            ("Why might a beginner compare liquidity and spreads before choosing a pair?", "They affect how easily a position may be entered or exited and its transaction cost.", ("They guarantee the direction of the next price move.", "They remove the possibility of losses.", "They determine the trader's tax rate everywhere."), "Liquidity and spreads influence trading costs and execution, but do not predict price direction."),
            ("How does the global Forex trading week generally operate?", "Activity moves across regional sessions for roughly 24 hours a day, five days a week.", ("Every currency pair trades continuously, including all weekends.", "Only one exchange opens for one hour each day.", "All sessions begin and end at the same local time worldwide."), "FX hours generally roll through regional centres on weekdays; provider hours and holidays can differ."),
            ("What is a session overlap?", "A period when the business hours of two regional financial centres coincide.", ("A period when all brokers close positions automatically.", "A guarantee that spreads will be zero.", "A type of currency conversion fee."), "Overlaps can coincide with more activity, though liquidity and volatility are not assured."),
            ("Which statement about major pairs is most accurate?", "Many commonly defined major pairs include USD, but costs and liquidity still vary.", ("Every major pair has identical spreads at every broker.", "Major pairs cannot lose value.", "A major pair is always suitable for every trader."), "Pair labels describe common trading conventions, not a guarantee about cost, risk, or suitability."),
        ),
    },
    {
        "key": "trade-mechanics",
        "title": "Module 2: Mechanics of a Trade",
        "category": "Trade Mechanics",
        "summary": "Learn pips, spreads, position sizes, long and short trades, and execution risk.",
        "order_index": 20,
        "image_url": "/learning-images/trade-mechanics.jpg",
        "image_alt": "A price chart with candlesticks and indicator lines.",
        "body": """
<h2>Pips and spreads</h2>
<p>A pip is a conventional unit for describing a small exchange-rate move. For many non-JPY pairs it is 0.0001; for many JPY pairs it is 0.01. Some platforms show fractional pips, and contract specifications should be checked. The spread is the difference between the bid and ask prices. It is one trading cost; commissions, financing, and slippage may also apply.</p>
<h2>Lots and contract sizes</h2>
<p>Position size describes the amount of base currency controlled. Common retail conventions call 100,000 units a standard lot, 10,000 a mini lot, and 1,000 a micro lot. Platform lot notation and contract sizes vary, so verify the provider's specifications. A smaller trade size can reduce exposure, but does not make a trade risk-free.</p>
<h2>Long and short</h2>
<p>A long position in a pair buys its base currency and benefits if the pair rises, before costs. A short position sells the base currency and benefits if the pair falls, before costs. The loss can grow if the price moves the other way. Stop orders can be affected by gaps or slippage and may not cap the loss at the requested price.</p>
<p><strong>Learning note:</strong> Position size should be considered together with stop distance, pip value, costs, and the possibility that execution differs from the requested price.</p>
<h2>Further reading</h2>
<ul><li><a href="https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/foreign">Investor.gov: Forex quotes, transaction costs, and risks</a></li><li><a href="https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/CustomerAdvisory_MustKnowForex.html">CFTC: leverage and margin risks</a></li></ul>
""",
        "questions": (
            ("For many non-JPY currency pairs, what is one conventional pip?", "A move of 0.0001 in the quoted exchange rate.", ("A move of 1.0000 in the quoted exchange rate.", "A move of 0.01 percent in every pair.", "A fixed cash amount that is identical for every position."), "Many non-JPY pairs use 0.0001 as a pip, but conventions and fractional-pip display vary."),
            ("For many JPY pairs, what is one conventional pip?", "A move of 0.01 in the quoted exchange rate.", ("A move of 0.0001 in every JPY pair.", "A move of 1,000 yen in the account balance.", "A fixed one-dollar fee."), "Many JPY pairs use 0.01 as a pip; check the instrument's quote convention."),
            ("What is the bid-ask spread?", "The difference between the bid price and ask price.", ("The difference between a trader's deposit and withdrawal.", "The maximum possible daily price move.", "The interest paid on every trade."), "The spread is the gap between the prices at which a provider quotes buying and selling."),
            ("Why does a wider spread matter to a trader?", "It generally increases the cost of entering and exiting a position.", ("It guarantees a better fill price.", "It means the trade cannot lose.", "It removes overnight financing charges."), "A wider spread raises transaction cost, all else equal; other costs and execution matter too."),
            ("In a common retail convention, what does one standard lot represent?", "100,000 units of the base currency.", ("1,000 units of the quote currency.", "10 units of the account currency.", "A guaranteed maximum loss of 1% of equity."), "A standard lot is commonly 100,000 base-currency units, but provider specifications should be checked."),
            ("Under common lot conventions, what is a micro lot?", "1,000 units of the base currency.", ("100,000 units of the base currency.", "One pip regardless of pair.", "A position with no margin requirement."), "A micro lot commonly represents 1,000 base-currency units; exact contract terms can vary."),
            ("What does going long EUR/USD mean?", "Buying EUR and selling USD, with the position benefiting if EUR/USD rises before costs.", ("Selling EUR and buying USD, with the position benefiting if EUR/USD rises.", "Buying both currencies so the price cannot change.", "Borrowing euros at a guaranteed fixed rate."), "A long EUR/USD position buys the base currency; a price decline can cause a loss."),
            ("When can a short position in a pair gain value before costs?", "When the pair price falls after the short position is opened.", ("Only when the pair price rises.", "Only when the market is closed.", "Whenever the spread widens."), "A short pair position generally benefits from a fall in the pair's quoted price, before costs."),
            ("What does a stop-loss order do, and what limitation should be understood?", "It requests an exit at a trigger, but a gap or slippage can produce a different fill.", ("It guarantees the requested price under all market conditions.", "It adds funds to prevent any loss.", "It turns a losing trade into a limit order automatically."), "Stop orders may execute at a different price during fast or gapped markets; provider rules vary."),
            ("Which inputs should be considered together when sizing a trade?", "Position size, stop distance, pip value, costs, and execution risk.", ("Only the account's leverage setting.", "Only the trader's preferred profit target.", "Only the number of trades made that day."), "Position size alone does not describe risk; distance, value per move, costs, and slippage matter."),
        ),
    },
    {
        "key": "orders-platforms-tools",
        "title": "Module 3: Orders, Platforms & Tools",
        "category": "Trading Tools",
        "summary": "Compare order types, charting platforms, brokers, and demo-account limitations.",
        "order_index": 30,
        "image_url": "/learning-images/trading-tools.jpg",
        "image_alt": "A laptop and phone displaying financial charts.",
        "body": """
<h2>Order types</h2>
<p>A market order requests execution as soon as possible at available prices. A limit order sets a maximum acceptable buy price or minimum acceptable sell price, and may not fill. A stop order activates after its trigger is reached; in many systems it then becomes a market order. Names and execution details differ by provider.</p>
<p>A stop-loss is an instruction intended to exit if price reaches a specified level. A take-profit instruction seeks to exit after a favorable move. Neither should be treated as a guarantee of execution at an exact price during gaps or fast markets.</p>
<h2>Platforms and charting</h2>
<p>Tools such as MetaTrader 5 and TradingView can display charts and help users practice analysis. A charting platform is not necessarily the broker or the venue that executes a trade. Learn the order ticket, contract specification, account currency, and fees before using any tool.</p>
<h2>Brokers and demo accounts</h2>
<p>Check a provider's authorization with the regulator responsible in the provider's jurisdiction and in your own jurisdiction. Read the terms for fees, withdrawals, custody, leverage, and dispute handling; a regulator's register is not a guarantee against loss. Demo or paper trading uses simulated funds and is useful for learning interfaces, but simulated fills and emotions can differ from live trading.</p>
<p><strong>Learning note:</strong> Do not share account credentials or send funds to an unverified person promising guaranteed returns.</p>
<h2>Further reading</h2>
<ul><li><a href="https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/CustomerAdvisory_MustKnowForex.html">CFTC: researching Forex dealers and recognizing risks</a></li><li><a href="https://www.tradingview.com/support/solutions/43000516466-paper-trading-main-functionality/">TradingView: paper-trading overview</a></li></ul>
""",
        "questions": (
            ("What does a market order generally request?", "Execution as soon as possible at prices currently available.", ("Execution only at a chosen price or better.", "Execution only after the market closes.", "A guaranteed fill at the last displayed price."), "A market order prioritizes execution, not a guaranteed exact price."),
            ("What is a key limitation of a limit order?", "It may not execute if the market does not reach its price or available liquidity is insufficient.", ("It always executes immediately.", "It guarantees a profit if filled.", "It cannot be cancelled by the user."), "A limit order controls the price condition but does not guarantee a fill."),
            ("What often happens after a stop-entry order is triggered?", "It becomes a market order, depending on the provider's rules.", ("It becomes a guaranteed limit order at the trigger price.", "It is cancelled automatically.", "It guarantees a take-profit."), "Many stop orders activate into market orders; exact handling varies by venue and provider."),
            ("What is the intended purpose of a stop-loss instruction?", "To request an exit when a specified adverse price level is reached.", ("To guarantee a maximum loss at an exact price.", "To increase leverage when the market moves against you.", "To close all trades at the end of every session."), "A stop-loss is an exit instruction, but gaps and slippage can change the fill price."),
            ("What is a take-profit order intended to do?", "Request an exit when a specified favorable price level is reached.", ("Guarantee that a trade will be profitable after all costs.", "Prevent all future drawdowns.", "Increase the position size after a loss."), "A take-profit sets an exit condition; execution and net outcome are not guaranteed."),
            ("Why should users distinguish a charting platform from a broker?", "A charting tool may display analysis without being the provider that holds or executes the account.", ("All charting platforms are financial regulators.", "A charting platform guarantees the accuracy of every broker quote.", "A charting platform eliminates fees."), "Charting, account services, and execution may be provided by different companies."),
            ("What is a useful first check when evaluating a broker?", "Verify its authorization with relevant regulators and review its terms and disciplinary history where available.", ("Choose the broker with the most social-media followers.", "Trust a guaranteed-return advertisement.", "Send a small payment to a private agent first."), "Regulatory status and the provider's terms should be checked; registration does not remove trading risk."),
            ("What does a demo or paper-trading account use?", "Simulated funds rather than the user's real trading capital.", ("A regulator-backed guarantee against loss.", "A live order that cannot be cancelled.", "A loan from the platform provider."), "Paper trading simulates activity with virtual funds and does not reproduce every live condition."),
            ("Why might live results differ from demo results?", "Execution, costs, liquidity, and the emotional effect of risking real money can differ.", ("Demo prices are legally guaranteed to match every live fill.", "Live accounts do not have spreads.", "Demo trading predicts future returns."), "Simulated conditions and behavior can differ from live trading, so demos do not prove future performance."),
            ("What is the safest response to someone promising guaranteed Forex profits?", "Treat the claim as a warning sign and independently verify the person and provider.", ("Share your login so they can demonstrate the strategy.", "Borrow money to increase the account balance.", "Ignore all provider terms if the returns sound high."), "Guaranteed high returns are a warning sign; protect credentials and verify claims independently."),
        ),
    },
    {
        "key": "reading-markets",
        "title": "Module 4: Reading the Markets (Analysis Basics)",
        "category": "Market Analysis",
        "summary": "Explore candlesticks, support and resistance, indicators, economic news, and trading styles.",
        "order_index": 40,
        "image_url": "/learning-images/market-analysis.jpg",
        "image_alt": "A laptop displaying a market analytics dashboard.",
        "body": """
<h2>Technical analysis</h2>
<p>A candlestick summarizes open, high, low, and close prices for a chosen interval. Support and resistance are areas where price has previously encountered buying or selling interest; they are not fixed barriers. Moving averages summarize past prices and lag by design. RSI is a momentum indicator. No chart pattern or indicator can guarantee what price will do next.</p>
<h2>Fundamental analysis</h2>
<p>Currency prices can respond to expected and actual changes in interest rates, inflation, employment, growth, and central-bank communication. Economic calendars help traders identify scheduled releases such as US Non-Farm Payrolls. Markets may move before a release as expectations change, and outcomes can be volatile or differ from forecasts.</p>
<h2>Trading styles</h2>
<p>Scalping typically targets very short moves, day trading usually closes positions within a day, and swing trading commonly holds positions for days or longer. Each style has different time, cost, and risk demands. There is no universally easiest or best style; suitability depends on circumstances, and no style ensures a positive result.</p>
<p><strong>Learning note:</strong> Historical tests can be misleading if costs, slippage, and overfitting are ignored. Past behavior does not guarantee future results.</p>
<h2>Further reading</h2>
<ul><li><a href="https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/CustomerAdvisory_MustKnowForex.html">CFTC: Forex market risks</a></li><li><a href="https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/foreign">Investor.gov: currency pricing and risks</a></li></ul>
""",
        "questions": (
            ("What four values does a standard candlestick summarize for an interval?", "Open, high, low, and close.", ("Bid, ask, spread, and commission.", "Entry, stop, target, and leverage.", "Inflation, interest, employment, and growth."), "Each candlestick represents the opening, highest, lowest, and closing prices for its interval."),
            ("How should support and resistance be interpreted?", "As possible price areas of interest, not guaranteed barriers.", ("As fixed levels that price can never cross.", "As official central-bank exchange rates.", "As orders that guarantee a reversal."), "These are analytical areas based on past behavior; price can move through them."),
            ("What is a common limitation of a moving average?", "It uses past prices and therefore tends to lag current market changes.", ("It predicts the exact next exchange rate.", "It removes all market noise without delay.", "It guarantees that a trend will continue."), "A moving average summarizes historical prices, so it reacts after some price movement has occurred."),
            ("What does RSI primarily measure?", "A momentum measure calculated from recent price changes.", ("A broker's available margin.", "The exact future value of a currency.", "The amount of commission charged."), "RSI is a momentum indicator; it does not guarantee a reversal or future return."),
            ("Which is an example of fundamental information that can affect currencies?", "Interest-rate decisions and central-bank communication.", ("The color of a chart background.", "The order of indicators in a menu.", "A trader's preferred position size."), "Rate expectations and central-bank communication can affect currency valuations, among other factors."),
            ("What is an economic calendar useful for?", "Seeing scheduled economic releases and their expected timing.", ("Knowing the exact direction of the market after each release.", "Guaranteeing a price at which an order will fill.", "Replacing the need to understand trade risk."), "Calendars show scheduled events; the market's response remains uncertain."),
            ("What is Non-Farm Payrolls (NFP) in a Forex context?", "A US employment report that can influence expectations and currency prices.", ("A broker's monthly commission statement.", "A measure of the EUR/USD spread.", "A rule that closes all Friday positions."), "NFP is a US labor-market release; price impact depends on expectations and broader conditions."),
            ("Which description best distinguishes technical and fundamental analysis?", "Technical analysis studies price behavior; fundamental analysis considers economic and policy factors.", ("Technical analysis guarantees timing; fundamental analysis guarantees direction.", "They are identical names for a stop order.", "Fundamental analysis applies only to chart colors."), "The approaches focus on different information and neither provides certainty."),
            ("Which statement about scalping, day trading, and swing trading is sound?", "They differ in typical holding period and demands; none is universally easiest or suitable.", ("Swing trading is guaranteed to be easiest for beginners.", "Scalping has no transaction costs.", "Day trading cannot incur losses overnight."), "Trading styles have different demands, and no style is best for every person or circumstance."),
            ("Why should a historical strategy test include costs and slippage?", "Ignoring them can make simulated performance look better than achievable results.", ("They guarantee future performance if included.", "They remove the need for out-of-sample testing.", "They make every strategy profitable."), "Costs and execution differences affect results; even careful tests cannot ensure future performance."),
        ),
    },
    {
        "key": "risk-management-psychology",
        "title": "Module 5: Risk Management & Psychology",
        "category": "Risk & Psychology",
        "summary": "Study position risk, leverage, margin, disciplined routines, and trading journals.",
        "order_index": 50,
        "image_url": "/learning-images/risk-journal.jpg",
        "image_alt": "A notebook and pencil on a desk for recording a trading plan.",
        "body": """
<h2>Risk per trade</h2>
<p>Some educational materials discuss risking a small percentage, such as 1% or 2%, of account equity on a planned trade. These figures are examples, not a universal rule, guarantee, or personalized recommendation. A stop level does not guarantee the final loss: gaps, slippage, fees, and leverage can make actual results differ. Only consider risking money you can afford to lose.</p>
<h2>Leverage and margin</h2>
<p>Leverage gives exposure larger than the funds committed as margin. It magnifies losses as well as gains. Margin is collateral required to open or maintain a position; a provider may close positions if requirements are no longer met. Rules and protections vary by jurisdiction and provider. Understand the maximum possible loss and contract terms before trading.</p>
<h2>Psychology and process</h2>
<p>Fear, greed, frustration, and overconfidence can lead to impulsive decisions, such as moving a stop or increasing size to recover a loss. A written plan and trading journal can record the rationale, size, stop, costs, outcome, and emotions for later review. A journal helps evaluate decisions; it cannot make a strategy profitable.</p>
<p><strong>Learning note:</strong> Forex is high risk and may not be appropriate for everyone. Nothing here is financial advice or a promise of results.</p>
<h2>Further reading</h2>
<ul><li><a href="https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/CustomerAdvisory_MustKnowForex.html">CFTC: leverage, margin, and dealer risks</a></li><li><a href="https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/foreign">Investor.gov: risks of Forex trading</a></li></ul>
""",
        "questions": (
            ("How should a 1% or 2% risk figure be treated in a trading lesson?", "As an example some traders discuss, not a universal rule or guarantee.", ("As a law that guarantees the account cannot lose more.", "As a recommendation suitable for every person.", "As a guarantee that a trade will be profitable."), "Percentage figures are educational examples, not personal advice or a guarantee of maximum loss."),
            ("If an account has $1,000, what is 1% of its balance arithmetically?", "$10.", ("$1.", "$100.", "$1,000."), "One percent of $1,000 is $10; this arithmetic does not mean actual loss is capped at that amount."),
            ("What does leverage do to exposure?", "It allows a position's notional exposure to exceed the funds posted, magnifying gains and losses.", ("It prevents losses beyond the spread.", "It removes the need for margin.", "It guarantees the trader's chosen return."), "Leverage increases exposure relative to committed funds and can magnify losses as well as gains."),
            ("What is margin in a leveraged trade?", "Funds held as collateral to open or maintain a position.", ("A guaranteed profit paid by the broker.", "A refund of all trading costs.", "A signal that the trade cannot lose."), "Margin is collateral; the provider's requirements and liquidation rules matter."),
            ("What can happen if an account no longer meets a provider's margin requirement?", "The provider may require more funds or close positions under its terms.", ("The provider must guarantee the position's original value.", "The trade becomes risk-free.", "The account automatically earns interest."), "Margin actions depend on provider terms and applicable rules; positions can be closed and losses may occur."),
            ("Why might a stop level fail to cap a trade's loss at the planned amount?", "A gap, slippage, and costs can cause execution at a different price.", ("Stops always execute at the exact requested price.", "Stops remove leverage from every account.", "The exchange rate cannot move through a stop."), "A stop is an instruction, not a guarantee of exact execution or a maximum cash loss."),
            ("What is one useful purpose of a trading journal?", "Recording decisions, risk, costs, outcomes, and emotions for later review.", ("Guaranteeing that every future trade wins.", "Replacing the need to define trade size.", "Hiding losses from account statements."), "A journal can support reflection and consistency, but cannot guarantee profitability."),
            ("Which is an example of a potentially impulsive response after a loss?", "Increasing position size to try to recover the loss quickly.", ("Reviewing the trade against a written plan.", "Recording the trade's costs and rationale.", "Pausing to assess whether the plan was followed."), "Increasing size to recover losses can compound risk and is often driven by emotion rather than a tested plan."),
            ("Why write down an entry, exit, and position-sizing plan before a trade?", "It can help make decisions consistent and easier to review afterward.", ("It makes the market follow the plan.", "It guarantees that a stop will fill at its requested price.", "It removes all psychological pressure."), "Planning can support discipline, but it cannot control market moves or guarantee an outcome."),
            ("Which statement best describes Forex risk?", "Losses can be substantial, and leveraged OTC trading may involve losing all invested funds or more, depending on terms and protections.", ("A demo account guarantees live profits.", "A regulated provider makes trading risk-free.", "A small deposit always limits the maximum loss to that deposit."), "Regulatory protections and loss limits differ; understand the provider's terms and the possibility of substantial losses."),
        ),
    },
    {
        "key": "trading-plan-review",
        "title": "Module 6: Building a Trading Plan & Reviewing Performance",
        "category": "Trading Process",
        "summary": "Build a repeatable practice plan and review decisions without assuming past results predict future ones.",
        "order_index": 60,
        "image_url": "/learning-images/trading-plan.jpg",
        "image_alt": "A written plan and chart notes for reviewing a trading process.",
        "body": """
<h2>What belongs in a trading plan?</h2>
<p>A written plan can describe the markets and timeframes you study, the conditions you need before considering a trade, how you estimate exposure and costs, and the situations in which you will stay out. A plan is a decision framework, not a forecast or a promise of results.</p>
<h2>Practice before risking money</h2>
<p>Demo accounts can help you learn platform functions and rehearse a process without placing live trades. Simulated fills, emotions, liquidity, and costs may differ from live trading, so demo results do not establish that a strategy will perform the same way with real money.</p>
<h2>Review decisions, not just outcomes</h2>
<p>After a practice session, record what you observed, why a setup did or did not meet your rules, the estimated costs, and whether you followed your process. A well-followed decision can still lose, and a profitable outcome can still result from a poor decision. Reviewing many examples is more informative than drawing conclusions from one trade.</p>
<h2>Keep records and revise carefully</h2>
<p>Change one part of a plan at a time and keep notes about why it changed. When reviewing historical examples, account for spreads, commissions, financing, slippage, and the risk of fitting rules to past prices. Past performance does not guarantee future results.</p>
<p><strong>Learning note:</strong> This material is educational, not individualized financial advice. Forex and leveraged products involve substantial risk.</p>
<h2>Further reading</h2>
<ul><li><a href="https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/CustomerAdvisory_MustKnowForex.html">CFTC: risks and due diligence for Forex customers</a></li><li><a href="https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/foreign">Investor.gov: Forex trading risks</a></li></ul>
""",
        "questions": (
            ("What is the main purpose of a written trading plan?", "To record decision rules and risk considerations for consistent practice and review.", ("To predict every market move.", "To guarantee that losses cannot occur.", "To ensure a broker fills every order at the requested price."), "A plan helps structure decisions and review; it cannot control markets or guarantee outcomes."),
            ("What can a demo account help a learner practice?", "Platform functions and a repeatable decision process in a simulated environment.", ("Guaranteed live execution quality.", "A strategy's certain future profitability.", "Avoiding all differences between simulated and live markets."), "Demo accounts can support practice, but simulated conditions may differ from live trading."),
            ("Why should a trade review include costs and slippage?", "They affect results and can make a plan look better on paper than in practice.", ("They reveal the exact next market direction.", "They guarantee a positive result when measured.", "They replace the need to record decisions."), "Trading costs and execution differences matter when evaluating a process."),
            ("Why review whether a decision followed the plan, in addition to its outcome?", "A good process can lose and a poor process can sometimes profit by chance.", ("The result of one trade proves a strategy works.", "Following a plan guarantees every trade will win.", "The outcome is the only useful information."), "Outcome and process are different; one result does not prove a method is reliable."),
            ("What is a careful way to revise a practice plan?", "Record the reason for a change and adjust it deliberately so the effect can be reviewed.", ("Change many rules after every losing trade.", "Keep changing rules until past data looks profitable.", "Remove risk limits whenever a setup looks strong."), "Documented, deliberate changes make it easier to understand what was tested."),
            ("What is a risk of fitting a strategy too closely to historical prices?", "It may appear effective on past examples but fail in different market conditions.", ("It guarantees future performance.", "It removes transaction costs automatically.", "It makes simulated data identical to live execution."), "Overfitting past data can produce rules that do not generalize to future conditions."),
            ("What should a learner conclude from a short run of profitable practice trades?", "It is limited evidence and does not guarantee future results.", ("The strategy is certain to stay profitable.", "Risk no longer needs to be considered.", "Live results will match simulated results exactly."), "A small sample cannot establish future performance or remove trading risk."),
            ("When might a trading plan say to stay out of a market?", "When the learner's stated conditions are not met or risks are not understood.", ("Whenever a trade has not won before.", "Only when a market has no price movement.", "Never, because a plan must always produce a trade."), "A decision framework can include conditions for not trading; taking no position is a valid choice."),
        ),
    },
)

STARTER_MODULES_BY_KEY = {module["key"]: module for module in STARTER_MODULES}
