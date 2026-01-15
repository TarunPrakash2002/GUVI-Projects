**SQL Queries used for analytics:**

1. To create the table according to the input dataset:

   USE marketing_analysis;

   CREATE TABLE marketing_customers (
    ID INT PRIMARY KEY,
    Year_Birth INT,
    Education VARCHAR(50),
    Marital_Status VARCHAR(50),
    Income DECIMAL(10,2),
    Kidhome INT,
    Teenhome INT,
    Dt_Customer DATE,
    Recency INT,
    
    MntWines DECIMAL(10,2),
    MntFruits DECIMAL(10,2),
    MntMeatProducts DECIMAL(10,2),
    MntFishProducts DECIMAL(10,2),
    MntSweetProducts DECIMAL(10,2),
    MntGoldProds DECIMAL(10,2),
    
    NumDealsPurchases INT,
    NumWebPurchases INT,
    NumCatalogPurchases INT,
    NumStorePurchases INT,
    NumWebVisitsMonth INT,
    
    AcceptedCmp1 INT,
    AcceptedCmp2 INT,
    AcceptedCmp3 INT,
    AcceptedCmp4 INT,
    AcceptedCmp5 INT,
    
    Response INT,
    Complain INT,
    Country VARCHAR(50),
    
    Age INT,
    Children INT,
    Total_Spend DECIMAL(10,2),
    Total_Purchases INT,
    
    Customer_Tenure_Days INT,
    Customer_Tenure_Months DECIMAL(6,1),

    High_Income INT,
    Young_Customer INT,
    Campaign_Responder INT,
    High_Web_Engagement INT,
    Family_Customer INT,
    High_Spender INT
);

2. **KPI - Response Rate:**

   USE marketing_analysis;

   SELECT 'High Income' AS segment, AVG(Response) AS response_rate
   FROM marketing_customers
   WHERE High_Income = 1

   UNION ALL

   SELECT 'High Spender', AVG(Response)
   FROM marketing_customers
   WHERE High_Spender = 1

   UNION ALL

   SELECT 'High Web Engagement', AVG(Response)
   FROM marketing_customers
   WHERE High_Web_Engagement = 1

   UNION ALL

   SELECT 'Young Customer', AVG(Response)
   FROM marketing_customers
   WHERE Young_Customer = 1

   UNION ALL

   SELECT 'Family Customer', AVG(Response)
   FROM marketing_customers
   WHERE Family_Customer = 1

   UNION ALL

   SELECT 'Campaign Responder', AVG(Response)
   FROM marketing_customers
   WHERE Campaign_Responder = 1;

3. **KPI - Average Spend by Segment:**

   SELECT 'High Income' AS segment, AVG(Total_Spend) AS avg_total_spend
   FROM marketing_customers
   WHERE High_Income = 1

   UNION ALL

   SELECT 'High Spender', AVG(Total_Spend)
   FROM marketing_customers
   WHERE High_Spender = 1

   UNION ALL

   SELECT 'Family Customer', AVG(Total_Spend)
   FROM marketing_customers
   WHERE Family_Customer = 1

   UNION ALL

   SELECT 'High Web Engagement', AVG(Total_Spend)
   FROM marketing_customers
   WHERE High_Web_Engagement = 1

   UNION ALL

   SELECT 'Young Customer', AVG(Total_Spend)
   FROM marketing_customers
   WHERE Young_Customer = 1

   UNION ALL

   SELECT 'Campaign Responder', AVG(Total_Spend)
   FROM marketing_customers
   WHERE Campaign_Responder = 1;

4. **KPI - Average Visits:**

   USE marketing_analysis;

   SELECT
    AVG(NumWebPurchases)      AS avg_web_purchases,
    AVG(NumStorePurchases)    AS avg_store_purchases,
    AVG(NumCatalogPurchases)  AS avg_catalog_purchases,
    AVG(NumDealsPurchases)    AS avg_deal_purchases,
    AVG(NumWebVisitsMonth)    AS avg_web_visits_per_month
   FROM marketing_customers
   WHERE High_Spender = 1;

5. **KPI - Product Category:**

   USE marketing_analysis;

   SELECT
    Response,
    AVG(MntWines) AS avg_wines,
    AVG(MntFruits) AS avg_fruits,
    AVG(MntMeatProducts) AS avg_meat,
    AVG(MntFishProducts) AS avg_fish,
    AVG(MntSweetProducts) AS avg_sweets,
    AVG(MntGoldProds) AS avg_gold
   FROM marketing_customers
   GROUP BY Response;

6. **Segment-level summary: Education:**

   USE marketing_analysis;

   SELECT
    Education,
    COUNT(*) AS customers,
    AVG(Response) AS response_rate,
    AVG(Total_Spend) AS avg_total_spend
   FROM marketing_customers
   GROUP BY Education
   ORDER BY response_rate DESC;

7. **Segment-level summary: Marital Status:**

   USE marketing_analysis;

   SELECT
    Marital_Status,
    COUNT(*) AS customers,
    AVG(Response) AS response_rate,
    AVG(Total_Spend) AS avg_total_spend
   FROM marketing_customers
   GROUP BY Marital_Status
   ORDER BY response_rate DESC;

8. **Segment-level summary: Country:**

   USE marketing_analysis;

   SELECT
    Country,
    COUNT(*) AS customers,
    AVG(Response) AS response_rate,
    AVG(Total_Spend) AS avg_total_spend
   FROM marketing_customers
   GROUP BY Country
   ORDER BY customers DESC;

9. **Segment-level summary: Age Range:**

    USE marketing_analysis;

  SELECT
    CASE
        WHEN Age < 30 THEN 'Under 30'
        WHEN Age BETWEEN 30 AND 45 THEN '30–45'
        WHEN Age BETWEEN 46 AND 60 THEN '46–60'
        ELSE '60+'
    END AS age_band,
    COUNT(*) AS customers,
    AVG(Response) AS response_rate,
    AVG(Total_Spend) AS avg_total_spend
   FROM marketing_customers
   GROUP BY age_band
   ORDER BY age_band;

10. **Segment-level summary: Income Range:**

    USE marketing_analysis;

  SELECT
    CASE
        WHEN Income < 30000 THEN 'Low Income'
        WHEN Income BETWEEN 30000 AND 75000 THEN 'Middle Income'
        ELSE 'High Income'
    END AS income_band,
    COUNT(*) AS customers,
    AVG(Response) AS response_rate,
    AVG(Total_Spend) AS avg_total_spend
  FROM marketing_customers
  GROUP BY income_band
  ORDER BY response_rate DESC;
