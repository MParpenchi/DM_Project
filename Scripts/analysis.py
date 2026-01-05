import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# ایجاد پوشه plots اگر وجود ندارد
if not os.path.exists('plots'):
    os.makedirs('plots')

# ۱. اتصال به دیتابیس با آدرس صحیح
conn = sqlite3.connect('DMpro/weather_5y_milan.db')

# ۲. خواندن داده‌ها از جدول فیلتر شده
query = "SELECT * FROM final_weather_accidents_filtered"
df = pd.read_sql_query(query, conn)
conn.close()

# ۳. انتخاب ستون‌های عددی برای کورلیشن (بر اساس اسکرین‌شات شما)
# ستون‌هایی مثل Anno و Mese چون عددی هستند اما ماهیت زمانی دارند در تحلیل همبستگی عددی می‌آیند
columns_to_analyze = [
    'avg_temp', 'total_rain', 'total_snow', 
    'rain_days', 'snow_days', 'Incidenti', 'Feriti', 'Morti'
]

# محاسبه ماتریس همبستگی
correlation_matrix = df[columns_to_analyze].corr()

# ۴. رسم Heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(correlation_matrix, annot=True, cmap='RdYlGn', center=0, fmt=".2f")
plt.title('Correlation Analysis: Milan Weather vs Traffic Accidents')

# ذخیره و نمایش
plt.savefig('plots/correlation_heatmap.png')
print("نمودار همبستگی در پوشه plots ذخیره شد.")
plt.show()

# نمایش همبستگی‌های مستقیم با تعداد حوادث برای چک کردن سریع
print("\nCorrelation with Incidenti (Accidents):")
print(correlation_matrix['Incidenti'].sort_values(ascending=False))

# گروه‌بندی داده‌ها بر اساس میزان بارش (Rain Intensity)
# دسته‌بندی بر اساس چارک‌ها (Quantiles) برای دقت بیشتر
df['Rain_Category'] = pd.qcut(df['total_rain'], q=3, labels=['Low Rain', 'Medium Rain', 'High Rain'])

# محاسبه میانگین تصادفات در هر دسته
rain_analysis = df.groupby('Rain_Category', observed=True)['Incidenti'].mean().reset_index()

# رسم نمودار ستونی
plt.figure(figsize=(10, 6))
sns.barplot(x='Rain_Category', y='Incidenti', data=rain_analysis, palette='Blues')

plt.title('Average Monthly Accidents by Rain Intensity')
plt.xlabel('Rainfall Level')
plt.ylabel('Average Number of Accidents')

# ذخیره نمودار
plt.savefig('plots/accidents_by_rain_intensity.png')
print("نمودار شدت بارندگی در پوشه plots ذخیره شد.")
plt.show()

# چاپ مقادیر برای گزارش
print("\nAverage Accidents per Category:")
print(rain_analysis)

# ۱. ایجاد یک ستون برای تشخیص ماه برفی از غیربرفی
df['Is_Snowy'] = df['total_snow'].apply(lambda x: 'Snowy Month' if x > 0 else 'No Snow')

# ۲. محاسبه میانگین تصادفات و مصدومین در هر حالت
snow_comparison = df.groupby('Is_Snowy', observed=True)[['Incidenti', 'Feriti']].mean().reset_index()

# ۳. رسم نمودار مقایسه‌ای
plt.figure(figsize=(10, 6))
sns.barplot(x='Is_Snowy', y='Incidenti', data=snow_comparison, palette='Purples')

plt.title('Average Monthly Accidents: Snowy vs Non-Snowy Months')
plt.xlabel('Condition')
plt.ylabel('Average Number of Accidents')

# ذخیره نمودار
plt.savefig('plots/snow_vs_accidents.png')
print("نمودار تحلیل برف در پوشه plots ذخیره شد.")
plt.show()

# چاپ مقادیر برای تحلیل دقیق‌تر
print("\nSnow Analysis Table:")
print(snow_comparison)

# ۱. ساخت یک ستون تاریخ برای محور افقی
df['Date'] = pd.to_datetime(df['Anno'].astype(str) + '-' + df['Mese'].astype(str) + '-01')

# ۲. رسم نمودار دو محوره (تعداد تصادفات در برابر میزان بارندگی)
fig, ax1 = plt.subplots(figsize=(14, 7))

# محور اول: تصادفات
color = 'tab:red'
ax1.set_xlabel('Year-Month')
ax1.set_ylabel('Monthly Accidents', color=color)
ax1.plot(df['Date'], df['Incidenti'], color=color, linewidth=2, marker='o', label='Accidents')
ax1.tick_params(axis='y', labelcolor=color)

# ایجاد محور دوم برای بارندگی
ax2 = ax1.twinx() 
color = 'tab:blue'
ax2.set_ylabel('Total Rainfall (mm)', color=color)
ax2.bar(df['Date'], df['total_rain'], color=color, alpha=0.3, width=20, label='Rainfall')
ax2.tick_params(axis='y', labelcolor=color)

plt.title('Milan: Monthly Accidents vs Rainfall Trends (2020-2024)')
fig.tight_layout()

# ذخیره نمودار
plt.savefig('plots/time_series_trends.png')
print("نمودار سری زمانی در پوشه plots ذخیره شد.")
plt.show()

from sklearn.linear_model import LinearRegression

# آماده سازی داده‌ها
X = df[['total_rain']].values
y = df['Incidenti'].values

# ساخت مدل
model = LinearRegression()
model.fit(X, y)

# چاپ نتایج در ترمینال
print(f"\nModel Result:")
print(f"Intercept: {model.intercept_:.2f}")
print(f"Slope (Rain Impact): {model.coef_[0]:.4f}")

# رسم نمودار
plt.figure(figsize=(10, 6))
plt.scatter(X, y, color='blue', alpha=0.5, label='Actual Data')
plt.plot(X, model.predict(X), color='red', linewidth=2, label='Regression Line')
plt.title('Regression Analysis: Rain vs Accidents')
plt.xlabel('Rainfall (mm)')
plt.ylabel('Accidents')
plt.legend()
plt.savefig('plots/regression_plot.png')
plt.show()


import numpy as np
from sklearn.preprocessing import PolynomialFeatures

# تبدیل داده‌ها به توان ۲ (برای ایجاد منحنی)
poly = PolynomialFeatures(degree=2)
X_poly = poly.fit_transform(X)

# آموزش مدل روی داده‌های منحنی
poly_model = LinearRegression()
poly_model.fit(X_poly, y)

# رسم منحنی روی نمودار
X_range = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
y_poly_pred = poly_model.predict(poly.transform(X_range))

plt.figure(figsize=(10, 6))
plt.scatter(X, y, color='blue', alpha=0.5, label='Actual Data')
plt.plot(X_range, y_poly_pred, color='green', linewidth=3, label='Non-linear (Polynomial) Fit')
plt.title('Non-linear Analysis: Rain vs Accidents')
plt.legend()
plt.savefig('plots/non_linear_regression.png')
plt.show()

# ۱. محاسبه نرخ جراحت (تعداد مجروح به ازای هر تصادف)
df['Injury_Rate'] = df['Feriti'] / df['Incidenti']

# ۲. گروه‌بندی بر اساس دسته‌بندی باران که قبلاً ساختیم
severity_rain = df.groupby('Rain_Category', observed=True)['Injury_Rate'].mean().reset_index()

# ۳. رسم نمودار ستونی برای شدت تصادفات
plt.figure(figsize=(10, 6))
sns.barplot(x='Rain_Category', y='Injury_Rate', data=severity_rain, palette='Oranges')

plt.title('Accident Severity: Average Injuries per Accident by Rain Level')
plt.xlabel('Rainfall Intensity')
plt.ylabel('Injury Rate (Injuries per Incident)')

# ذخیره نمودار
plt.savefig('plots/accident_severity_rate.png')
plt.show()

# چاپ اعداد برای گزارش
print("\n--- Severity Analysis Result ---")
print(severity_rain)

# ۱. تعریف تابع برای تعیین فصل بر اساس ماه
def get_season(month):
    if month in [12, 1, 2]: return 'Winter'
    elif month in [3, 4, 5]: return 'Spring'
    elif month in [6, 7, 8]: return 'Summer'
    else: return 'Autumn'

# ۲. اعمال تابع روی ستون Mese
df['Season'] = df['Mese'].apply(get_season)

# ۳. محاسبه میانگین تصادفات در هر فصل
seasonal_analysis = df.groupby('Season')['Incidenti'].mean().reindex(['Spring', 'Summer', 'Autumn', 'Winter']).reset_index()

# ۴. رسم نمودار
plt.figure(figsize=(10, 6))
sns.lineplot(x='Season', y='Incidenti', data=seasonal_analysis, marker='o', linewidth=3, color='green')

plt.title('Average Monthly Accidents by Season in Milan')
plt.ylabel('Average Accidents')
plt.grid(True, linestyle='--', alpha=0.6)

# ذخیره
plt.savefig('plots/seasonal_accidents.png')
plt.show()

print("\n--- Seasonal Analysis Result ---")
print(seasonal_analysis)


# ۱. پیدا کردن ۵ ماهی که بیشترین تعداد تصادف در آن‌ها رخ داده است
top_accidents = df.sort_values(by='Incidenti', ascending=False).head(5)

print("\n--- Top 5 Worst Months for Accidents ---")
print(top_accidents[['Anno', 'Mese', 'Incidenti', 'total_rain', 'weather_condition']])

# ۲. رسم یک نمودار پراکندگی برای دیدن نقاط پرت (Outliers)
plt.figure(figsize=(10, 6))
sns.boxplot(x=df['Incidenti'], color='salmon')
plt.title('Distribution of Monthly Accidents (Identifying Outliers)')
plt.xlabel('Number of Accidents')

# ذخیره
plt.savefig('plots/accidents_outliers.png')
plt.show()

from sklearn.metrics import r2_score

# ۱. محاسبه پیش‌بینی‌ها
y_pred = model.predict(X)

# ۲. محاسبه شاخص R-squared
r2 = r2_score(y, y_pred)

print("\n--- Final Model Accuracy ---")
print(f"R-squared Score: {r2:.4f}")

# ۳. یک متن تحلیل نهایی برای گزارش
if r2 < 0.1:
    print("Interpretation: Rain is a contributing factor, but urban traffic complexity is dominant.")
else:
    print("Interpretation: Rain has a significant and measurable impact on accident variance.")