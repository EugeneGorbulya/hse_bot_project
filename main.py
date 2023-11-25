import pandas as pd
import io
import dataframe_image as dfi
import numpy as np
import plotly
import matplotlib.pyplot as plt
from scipy import stats as st
import asyncio
import logging
import sys
from os import getenv
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram import F
from aiogram.types import Message, FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.markdown import hbold
from aiogram.filters.command import Command
from tok import token
import seaborn as sns
#Импортируем все нужные библиотеки

TOKEN = token

dp = Dispatcher()
#Dispatcher — это класс, который играет центральную роль в управлении и обработке входящих событий


df = pd.read_csv("salaries.csv")
df_without_small_countries = df.groupby("company_location").filter(lambda x: len(x) > 20)
#Работа с БДшками


button1 = KeyboardButton(text="Get stats")
button2 = KeyboardButton(text="Show data")
button3 = KeyboardButton(text="Check hypothesis")
ex = KeyboardButton(text="Back to menu")
menu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[button1, button2, button3]])
b1 = KeyboardButton(text="Check 1")
b2 = KeyboardButton(text="Check 2")
b3 = KeyboardButton(text="Check 3")
hypos = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[b1, b2, b3], [ex]])
but1 = KeyboardButton(text="Graphic 1")
but2 = KeyboardButton(text="Graphic 2")
but3 = KeyboardButton(text="Graphic 3")
datas = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[but1, but2, but3], [ex]])
#Создал все кнопки, которые буду потом использовать


@dp.message(CommandStart()) #Пишем перед функциями где будем работать с входящими сообщениями @dp.message()
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")
    info = "The dataset contains one table structured as follow:\nwork_year: The year the salary was paid.\nexperience_level: The experience level in the job during the year with the following possible values:\nEN: Entry-level / Junior\nMI: Mid-level / Intermediate\nSE: Senior-level / Expert\nEX: Executive-level / Director\nemployment_type: The type of employement for the role:\nPT: Part-time\nFT: Full-time\nCT: Contract\nFL: Freelance\nbjob_title: The role worked in during the year.\nsalary: The total gross salary amount paid.\nsalary_currency: The currency of the salary paid as an ISO 4217 currency code.\nsalary_in_usd: The salary in USD (FX rate divided by avg. USD rate for the respective year via fxdata.foorilla.com).\nemployee_residence: Employee's primary country of residence in during the work year as an ISO 3166 country code.\nremote_ratio: The overall amount of work done remotely, possible values are as follows:\n0: No remote work (less than 20%)\n50: Partially remote\n100: Fully remote (more than 80%)\ncompany_location: The country of the employer's main office or contracting branch as an ISO 3166 country code.\ncompany_size: The average number of people that worked for the company during the year:\nS: less than 50 employees (small)\nM: 50 to 250 employees (medium)\nL: more than 250 employees (large)"
    #info - описание содержания БДшки
    await message.answer(info)
    dfi.export(df.head(5), "start.png")
    #dfi - библа которая сохраняет DataFrame в виде картинки, можно указать путь
    photo = FSInputFile("start.png") #берет файл путь до которого ты указываешь
    await message.answer_photo(photo=photo, caption="Part of DataFrame", reply_markup=menu)
    #caption - подпись к фото
    #reply_markup - говорит какие кнопки использовать

@dp.message(F.text.lower() == "back to menu")
async def back_to_menu(message: Message) -> None:
    await message.answer("Menu", reply_markup=menu)
#создаю общую функцию для выхода в меню

@dp.message(F.text.lower() == "get stats")
async def get_stats(message: Message) -> None:
    #df.info() так просто не получится сохранить как картинку, так как у него тип данных не DataFrame
    buffer = io.StringIO()
    df.info(buf=buffer)
    s = buffer.getvalue()
    lines = [line.split() for line in s.splitlines()[3:-2]]#Обрезаем лишние строчки, которые мешают сделать dataFrame
    info_df = pd.DataFrame(lines) #Сохраняем в виде DataFrame
    dfi.export(info_df, "info.png")#Cохраняем как картинку
    describe_df = df.describe() #df.describe() в отличии от df.info() является DataFrame, поэтому сохраняем как раньше
    dfi.export(describe_df, "describe.png")
    photo1 = FSInputFile("info.png")
    await message.answer_photo(photo=photo1, caption="Info")
    photo2 = FSInputFile("describe.png")
    await message.answer_photo(photo=photo2, caption="Describe")

@dp.message(F.text.lower() == "show data")
async def show_data(message: Message) -> None:
    await message.answer("We have 3 graphics of Data:\n1)Count of jobs depending on year\n2)Comparison of Europe and America\n3)Salary in dollars depending on the position", reply_markup=datas)
    #Описываем какие графики у нас есть и вызываем кнопки для их вывода

@dp.message(F.text.lower() == "graphic 1")
async def show_data1(message: Message) -> None:
    df["work_year"] = df["work_year"].astype('int')
    plt.figure(figsize = (8, 6)) #Фиксируем размер для графика перед тем как его рисовать(делать это перед каждым графиком, так как она сохраняется между ними)
    df.groupby("work_year").count().reset_index().plot.bar(x = "work_year", y = "job_title")
    plt.title("Count of jobs")
    plt.xlabel("Year")
    plt.ylabel("Count")
    plt.savefig("cnt_jobs.png") #Строим графики из коллабы и сохраняем их с помощью savefig
    plt.clf() #Обязательно не забыть очистить после этого график, так как они могут меняться друг из-за друга
    photo = FSInputFile("cnt_jobs.png")
    await message.answer_photo(photo=photo, reply_markup=datas)

@dp.message(F.text.lower() == "graphic 2")
async def show_data2(message: Message) -> None:
    df_in_US = df_without_small_countries.loc[df_without_small_countries["company_location"] == "US"]
    df_in_EU = df_without_small_countries.loc[df_without_small_countries["company_location"].isin(["GB", "ES", "DE", "FR"])]
    list_of_year = [2020, 2021, 2022, 2023]
    list_of_mean = [df_in_US.loc[df_in_US["work_year"] == 2020]["salary_in_usd"].mean(),
                       df_in_US.loc[df_in_US["work_year"] == 2021]["salary_in_usd"].mean(),
                       df_in_US.loc[df_in_US["work_year"] == 2022]["salary_in_usd"].mean(),
                       df_in_US.loc[df_in_US["work_year"] == 2023]["salary_in_usd"].mean()]
    list_of_min = [df_in_US.loc[df_in_US["work_year"] == 2020]["salary_in_usd"].min(),
                       df_in_US.loc[df_in_US["work_year"] == 2021]["salary_in_usd"].min(),
                       df_in_US.loc[df_in_US["work_year"] == 2022]["salary_in_usd"].min(),
                       df_in_US.loc[df_in_US["work_year"] == 2023]["salary_in_usd"].min()]
    list_of_max = [df_in_US.loc[df_in_US["work_year"] == 2020]["salary_in_usd"].max(),
                       df_in_US.loc[df_in_US["work_year"] == 2021]["salary_in_usd"].max(),
                       df_in_US.loc[df_in_US["work_year"] == 2022]["salary_in_usd"].max(),
                       df_in_US.loc[df_in_US["work_year"] == 2023]["salary_in_usd"].max()]
    plt.figure(figsize = (8, 6))
    plt.plot(list_of_year, list_of_mean, color = "blue", label = "mean salary in US", linestyle = "--", linewidth = 1.0)
    plt.plot(list_of_year, list_of_min, color = "blue", label = "min salary in US", linestyle = ":", linewidth = 1.0)
    plt.plot(list_of_year, list_of_max, color = "blue", label = "max salary in US", linewidth = 1.0)
    list_of_mean_EU = [df_in_EU.loc[df_in_EU["work_year"] == 2020]["salary_in_usd"].mean(),
                       df_in_EU.loc[df_in_EU["work_year"] == 2021]["salary_in_usd"].mean(),
                       df_in_EU.loc[df_in_EU["work_year"] == 2022]["salary_in_usd"].mean(),
                       df_in_EU.loc[df_in_EU["work_year"] == 2023]["salary_in_usd"].mean()]
    list_of_min_EU = [df_in_EU.loc[df_in_EU["work_year"] == 2020]["salary_in_usd"].min(),
                       df_in_EU.loc[df_in_EU["work_year"] == 2021]["salary_in_usd"].min(),
                       df_in_EU.loc[df_in_EU["work_year"] == 2022]["salary_in_usd"].min(),
                       df_in_EU.loc[df_in_EU["work_year"] == 2023]["salary_in_usd"].min()]
    list_of_max_EU = [df_in_EU.loc[df_in_EU["work_year"] == 2020]["salary_in_usd"].max(),
                       df_in_EU.loc[df_in_EU["work_year"] == 2021]["salary_in_usd"].max(),
                       df_in_EU.loc[df_in_EU["work_year"] == 2022]["salary_in_usd"].max(),
                       df_in_EU.loc[df_in_EU["work_year"] == 2023]["salary_in_usd"].max()]
    plt.plot(list_of_year, list_of_mean_EU, color = "red", label = "mean salary in EU", linestyle = "--", linewidth = 1.0)
    plt.plot(list_of_year, list_of_min_EU, color = "red", label = "min salary in EU", linestyle = ":", linewidth = 1.0)
    plt.plot(list_of_year, list_of_max_EU, color = "red", label = "max salary in EU", linewidth = 1.0)
    plt.xticks(list_of_year)
    plt.xlabel("Year")
    plt.ylabel("Salary in USD")
    plt.title("Comparison of Europe and America")
    plt.legend()
    plt.savefig("comparison.png")
    plt.clf() #Всё тоже самое что и в graphic 1
    photo = FSInputFile("comparison.png")
    await message.answer_photo(photo=photo, reply_markup=datas)


@dp.message(F.text.lower() == "graphic 3")
async def show_data3(message: Message) -> None:
    df_most = df_without_small_countries.loc[df_without_small_countries["company_location"] == "US"]
    df_without_EX = df_most.loc[df_most["experience_level"].isin(["EN", "MI", "SE"])]
    plt.figure(figsize = (27,15))
    sns.boxplot(data=df_without_EX, y="job_title", x="salary_in_usd")
    plt.ylabel("Name of work")
    plt.xlabel("Salary in USD")
    plt.title("Salary in dollars depending on the position")
    plt.savefig("dependings.png")
    plt.clf() #Всё тоже самое что и выше
    photo = FSInputFile("dependings.png")
    await message.answer_photo(photo=photo, reply_markup=datas)

@dp.message(F.text.lower() == "check hypothesis")
async def check_hypo(message: Message) -> None:
    await message.answer("We have 3 hypothesis:\n1)Data Engeneer Middle and more == Data Scientist Middle and more\n2)Employees in small and middle have the same salary as employees in large companies\n3)In US employees have the same salary as employees in EU", reply_markup=hypos)
    #Описываем гипотезы и вызываем кнопки

@dp.message(F.text.lower() == "check 1")
async def check_hypo1(message: Message) -> None:
    df_engineers = df_without_small_countries.loc[df_without_small_countries["job_title"] == "Data Engineer"]
    df_engineers.loc[df_engineers["experience_level"].isin(['MI', 'SE'])]
    df_scientists = df_without_small_countries.loc[df_without_small_countries["job_title"] == "Data Scientist"]
    df_scientists.loc[df_scientists["experience_level"].isin(['MI', 'SE'])]
    ans = check_hypothesis(df_engineers["salary_in_usd"], df_scientists["salary_in_usd"])
    #Вызываем проверку гипотезы и выводим результат, снова пишем кнопки
    await message.answer(ans, reply_markup=hypos)

@dp.message(F.text.lower() == "check 2")
async def check_hypo1(message: Message) -> None:
    df_nonbig_comp = df_without_small_countries.loc[df_without_small_countries["company_size"].isin(["S", "M"])]
    df_big_comp = df_without_small_countries.loc[df_without_small_countries["company_size"].isin(["L"])]
    ans = check_hypothesis(df_big_comp["salary_in_usd"], df_nonbig_comp["salary_in_usd"])
    await message.answer(ans, reply_markup=hypos)

@dp.message(F.text.lower() == "check 3")
async def check_hypo1(message: Message) -> None:
    df_in_US = df_without_small_countries.loc[df_without_small_countries["company_location"] == "US"]
    df_in_EU = df_without_small_countries.loc[df_without_small_countries["company_location"].isin(["GB", "ES", "DE", "FR"])]
    ans = check_hypothesis(df_in_US["salary_in_usd"], df_in_EU["salary_in_usd"])
    await message.answer(ans, reply_markup=hypos)

async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API␣˓→calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)

def check_hypothesis(series_1: pd.Series, series_2: pd.Series, alpha=0.05) -> str:
    #Эту функцию мы писали на паре раньше
    series_1.dropna(inplace=True)
    series_2.dropna(inplace=True)
    std1 = series_1.std()
    std2 = series_2.std()
    result = st.ttest_ind(series_1, series_2, equal_var=(std1==std2))
    if result.pvalue < alpha:
        return "Можем отвергнуть гипотезу"
    else:
        return "Не можем отвергнуть гипотезу"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
