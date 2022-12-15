---
title: "climatechange-newswhippull"
author: "adl"
date: "2022-10-20"
output: github_document
---
```{r setup, include=FALSE}
knitr::opts_chunk$set(echo = TRUE)
knitr::opts_chunk$set(warning = FALSE)
```

```{r, warning=FALSE, message=FALSE, echo=FALSE}
library(httr)
library(jsonlite)
library(devtools)
library(urltools)
library(readr)
library(dplyr)
library(magrittr)
library(tidyr)
library(tidyverse)
library(lubridate)
library(scales)
library(ggplot2)
library(wesanderson)
library(ggthemes)
```

1. Create a function to get popular articles from Newswhip API with search words
- Create an object for maximum number of articles for each day
```{r}
num_articles <- 5000
```
- Create a variable with API key
```{r, echo=FALSE}
api_key <- 'XXXXXX'
```
- Create API endpoint
```{r}
api_endpoint <- paste0('https://api.newswhip.com/v1/articles?key=', api_key)
```
- Write the function
```{r}
get_newswhip_articles <- function(api_key, limit, start_time, end_time) {
  api_endpoint <- paste0('https://api.newswhip.com/v1/articles?key=', api_key)          
  data <- paste0('{\"filters\": [\"language:en AND country_code:us AND ((climate change) OR (climate crisis) OR (climate effects) OR (climate hoax) OR (climate policy) OR (climate resilience) OR (climate science) OR (climate summit) OR (global warming) OR (greenhouse gas) OR (greenhouse gases) OR (IPCC) OR (green energy) OR (climate hypocrisy) OR (paris agreement) OR (paris climate) OR (net zero) OR (net-zero) OR (COP26) OR (climate conversation) OR (climate test) OR (climate gap) OR (climate activists) OR (climate activist) OR (clean energy) OR (climate negotiations) OR (climate deal) OR (green new deal) OR (climate conference) OR (green technology) OR (green tech) OR (climate fearmongering) OR (climate fears) OR (climate anxiety) OR (carbon capture))\"],
                           \"size\": ', limit, ', 
                           \"from\": ', start_time, ',
                           \"to\": ', end_time, ',
                           \"search_full_text\": true,
                           \"find_related\": false}')
  r <- httr::POST(api_endpoint, body = data)
  httr::stop_for_status(r)         
  jsonlite::fromJSON(httr::content(r, "text", encoding = "UTF-8"), flatten = TRUE)$articles          
}
```
- Set the dates for the search
```{r}
days<-as.character(as.Date(as.Date("2017-01-01"):as.Date("2022-09-01"), origin="1970-01-01"))
```
- Write and run the loop
```{r}
mylist <- list()
for (i in days) {
  print("now running days:")
  print (i)
  start_time <- as.numeric(as.POSIXct(paste(i, "00:00:00 EST", sep=" "))) * 1000
  end_time <- as.numeric(as.POSIXct(paste(as.Date(paste(i))+1,  "00:00:00 EST", sep=" "))) * 1000 - 1
  data_temp <- get_newswhip_articles(api_key = api_key, limit = num_articles, start_time = start_time, end_time = end_time)
  data_temp$date_time <- as.POSIXct(round(data_temp$publication_timestamp/1000), origin="1970-01-01")
  data_temp$date <- as.Date(as.POSIXct(round(data_temp$publication_timestamp/1000), origin="1970-01-01"))
  data_temp$relatedStories <- NULL
  data_temp$topics <- NULL
  data_temp$authors <- NULL
  data_temp$entities <- NULL
  data_temp$videos <- NULL
  try(data_temp<- data_temp %>% dplyr::select(delta_time, 
                                       recent_fb_counts, 
                                       recent_tw_counts, 
                                       predicted_interactions, 
                                       predicted_timestamp, 
                                       uuid, 
                                       publication_timestamp, 
                                       link, 
                                       headline, 
                                       excerpt, 
                                       keywords, 
                                       image_link, 
                                       has_video, 
                                       nw_score, 
                                       max_nw_score, 
                                       fb_data.total_engagement_count, 
                                       fb_data.likes, 
                                       fb_data.comments, 
                                       fb_data.shares, 
                                       fb_data.total_count_delta, 
                                       fb_data.delta_period, 
                                       fb_data.delta_period_unit, 
                                       tw_data.tw_count, 
                                       tw_data.total_count_delta, 
                                       tw_data.delta_period, 
                                       tw_data.delta_period_unit, 
                                       li_data.li_count, 
                                       li_data.total_count_delta, 
                                       li_data.delta_period, 
                                       li_data.delta_period_unit, 
                                       pi_data.pi_count, 
                                       pi_data.delta_period, 
                                       pi_data.delta_period_unit, 
                                       source.publisher, 
                                       source.domain, 
                                       source.link, 
                                       source.country, 
                                       source.country_code, 
                                       source.language, 
                                       date_time, 
                                       date))
  mylist[[i]] <- data_temp
  }
```
- Bind the list to a dataframe and save for backup
```{r}
data_temp1 <- do.call("rbind",mylist)%>%data.frame()
#save(data_temp, file="Rda/Climate_NewsWhip_Master_090222.Rda")
```
- Clean duplicate UUID and links, sum engagement and add index
```{r}
dataclimateMaster<- data_temp1 %>%
  distinct(link,.keep_all = TRUE)%>%
  distinct(uuid,.keep_all = TRUE) %>%
  tibble::rowid_to_column(dataclimateMaster, "master_index") %>%
  rowwise() %>%
  mutate(engagement = sum(fb_data.total_engagement_count, 
                          tw_data.tw_count,
                          li_data.li_count,
                          pi_data.pi_count)) 
dataclimateMaster$dateMONTH <- format(as.Date(dataclimateMaster$date), "%Y-%m")
dataclimateMaster$url_to_test <- paste(suffix_extract(domain(dataclimateMaster$link))$domain, suffix_extract(domain(dataclimateMaster$link))$suffix, sep = ".")

save(dataclimateMaster, file="Rda/Climate_Newswhip_Master.Rda")
```
- Add the MBFC and NG list updated by Erik Nisbet and save again
```{r}
load("Rda/MBFC_NG_Erik_091922.Rda")

dataclimateMaster <- left_join(dataclimateMaster, datC, by = c("url_to_test"))
names(dataclimateMaster)
save(dataclimateMaster, file="Rda/Climate_Newswhip_Master.Rda")
```
2. Seperate to months for scraping, if you have have computer space and time you can run it as one csv. We seperated them and ran them simultaneously for the purpose of time and memory. 
```{r}
myscrape <- df %>%
  dplyr::select(master_index, link, date, dateMONTH)
rm(df) # to save space
gc() #to clean up memory
```
- 2017
```{r}
myscrape1 <-  myscrape %>%
  filter(dateMONTH=='2017-01' | dateMONTH=='2017-02')
min(myscrape1$date)
max(myscrape1$date)
write.csv(myscrape1, file="CSV/CC_Scrape_1.csv", row.names = FALSE)
rm(myscrape1)

myscrape2 <-  myscrape %>%
  filter(dateMONTH=='2017-03' | dateMONTH=='2017-04')
min(myscrape2$date)
max(myscrape2$date)
write.csv(myscrape2, file="CSV/CC_Scrape_2.csv", row.names = FALSE)
rm(myscrape2)

myscrape3 <-  myscrape %>%
  filter(dateMONTH=='2017-05' | dateMONTH=='2017-06')
min(myscrape3$date)
max(myscrape3$date)
write.csv(myscrape3, file="CSV/CC_Scrape_3.csv", row.names = FALSE)
rm(myscrape3)

myscrape4 <-  myscrape %>%
  filter(dateMONTH=='2017-07' | dateMONTH=='2017-08')
min(myscrape4$date)
max(myscrape4$date)
write.csv(myscrape4, file="CSV/CC_Scrape_4.csv", row.names = FALSE)
rm(myscrape4)

myscrape5 <-  myscrape %>%
  filter(dateMONTH=='2017-09' | dateMONTH=='2017-10')
min(myscrape5$date)
max(myscrape5$date)
write.csv(myscrape5, file="CSV/CC_Scrape_5.csv", row.names = FALSE)
rm(myscrape5)

myscrape6 <-  myscrape %>%
  filter(dateMONTH=='2017-11' | dateMONTH=='2017-12')
min(myscrape6$date)
max(myscrape6$date)
write.csv(myscrape6, file="CSV/CC_Scrape_6.csv", row.names = FALSE)
rm(myscrape6)
```
- 2018
```{r}
myscrape7 <-  myscrape %>%
  filter(dateMONTH=='2018-01' | dateMONTH=='2018-02')
min(myscrape7$date)
max(myscrape7$date)
write.csv(myscrape7, file="CSV/CC_Scrape_7.csv", row.names = FALSE)
rm(myscrape7)

myscrape8 <-  myscrape %>%
  filter(dateMONTH=='2018-03' | dateMONTH=='2018-04')
min(myscrape8$date)
max(myscrape8$date)
write.csv(myscrape8, file="CSV/CC_Scrape_8.csv", row.names = FALSE)
rm(myscrape2)

myscrape9 <-  myscrape %>%
  filter(dateMONTH=='2018-05' | dateMONTH=='2018-06')
min(myscrape9$date)
max(myscrape9$date)
write.csv(myscrape9, file="CSV/CC_Scrape_9.csv", row.names = FALSE)
rm(myscrape9)

myscrape10 <-  myscrape %>%
  filter(dateMONTH=='2018-07' | dateMONTH=='2018-08')
min(myscrape10$date)
max(myscrape10$date)
write.csv(myscrape10, file="CSV/CC_Scrape_10.csv", row.names = FALSE)
rm(myscrape10)

myscrape11 <-  myscrape %>%
  filter(dateMONTH=='2018-09' | dateMONTH=='2018-10')
min(myscrape11$date)
max(myscrape11$date)
write.csv(myscrape11, file="CSV/CC_Scrape_11.csv", row.names = FALSE)
rm(myscrape11)

myscrape12 <-  myscrape %>%
  filter(dateMONTH=='2018-11' | dateMONTH=='2018-12')
min(myscrape12$date)
max(myscrape12$date)
write.csv(myscrape12, file="CSV/CC_Scrape_12.csv", row.names = FALSE)
rm(myscrape12)
```
- 2019
```{r}
myscrape13 <-  myscrape %>%
  filter(dateMONTH=='2019-01' | dateMONTH=='2019-02')
min(myscrape13$date)
max(myscrape13$date)
write.csv(myscrape13, file="CSV/CC_Scrape_13.csv", row.names = FALSE)
rm(myscrape13)

myscrape14 <-  myscrape %>%
  filter(dateMONTH=='2019-03' | dateMONTH=='2019-04')
min(myscrape14$date)
max(myscrape14$date)
write.csv(myscrape14, file="CSV/CC_Scrape_14.csv", row.names = FALSE)
rm(myscrape14)

myscrape15<-  myscrape %>%
  filter(dateMONTH=='2019-05' | dateMONTH=='2019-06')
min(myscrape9$date)
max(myscrape9$date)
write.csv(myscrape9, file="CSV/CC_Scrape_15.csv", row.names = FALSE)
rm(myscrape15)

myscrape16 <-  myscrape %>%
  filter(dateMONTH=='2019-07' | dateMONTH=='2019-08')
min(myscrape16$date)
max(myscrape16$date)
write.csv(myscrape16, file="CSV/CC_Scrape_16.csv", row.names = FALSE)
rm(myscrape16)

myscrape17 <-  myscrape %>%
  filter(dateMONTH=='2019-09' | dateMONTH=='2019-10')
min(myscrape17$date)
max(myscrape17$date)
write.csv(myscrape17, file="CSV/CC_Scrape_17.csv", row.names = FALSE)
rm(myscrape17)

myscrape18 <-  myscrape %>%
  filter(dateMONTH=='2019-11' | dateMONTH=='2019-12')
min(myscrape18$date)
max(myscrape18$date)
write.csv(myscrape18, file="CSV/CC_Scrape_18.csv", row.names = FALSE)
rm(myscrape18)
```
- 2020
```{r}
myscrape19 <-  myscrape %>%
  filter(dateMONTH=='2020-01' | dateMONTH=='2020-02')
min(myscrape19$date)
max(myscrape19$date)
write.csv(myscrape19, file="CSV/CC_Scrape_19.csv", row.names = FALSE)
rm(myscrape19)

myscrape20 <-  myscrape %>%
  filter(dateMONTH=='2020-03' | dateMONTH=='2020-04')
min(myscrape20$date)
max(myscrape20$date)
write.csv(myscrape20, file="CSV/CC_Scrape_20.csv", row.names = FALSE)
rm(myscrape20)

myscrape21<-  myscrape %>%
  filter(dateMONTH=='2020-05' | dateMONTH=='2020-06')
min(myscrape9$date)
max(myscrape9$date)
write.csv(myscrape9, file="CSV/CC_Scrape_21.csv", row.names = FALSE)
rm(myscrape21)

myscrape22 <-  myscrape %>%
  filter(dateMONTH=='2020-07' | dateMONTH=='2020-08')
min(myscrape22$date)
max(myscrape22$date)
write.csv(myscrape22, file="CSV/CC_Scrape_22.csv", row.names = FALSE)
rm(myscrape22)

myscrape23 <-  myscrape %>%
  filter(dateMONTH=='2020-09' | dateMONTH=='2020-10')
min(myscrape23$date)
max(myscrape23$date)
write.csv(myscrape23, file="CSV/CC_Scrape_23.csv", row.names = FALSE)
rm(myscrape23)

myscrape24 <-  myscrape %>%
  filter(dateMONTH=='2020-11' | dateMONTH=='2020-12')
min(myscrape24$date)
max(myscrape24$date)
write.csv(myscrape24, file="CSV/CC_Scrape_24.csv", row.names = FALSE)
rm(myscrape24)
```
- 2021
```{r}
myscrape25 <-  myscrape %>%
  filter(dateMONTH=='2021-01' | dateMONTH=='2021-02')
min(myscrape25$date)
max(myscrape25$date)
write.csv(myscrape25, file="CSV/CC_Scrape_25.csv", row.names = FALSE)
rm(myscrape25)

myscrape26 <-  myscrape %>%
  filter(dateMONTH=='2021-03' | dateMONTH=='2021-04')
min(myscrape26$date)
max(myscrape26$date)
write.csv(myscrape26, file="CSV/CC_Scrape_26.csv", row.names = FALSE)
rm(myscrape26)

myscrape27<-  myscrape %>%
  filter(dateMONTH=='2021-05' | dateMONTH=='2021-06')
min(myscrape9$date)
max(myscrape9$date)
write.csv(myscrape9, file="CSV/CC_Scrape_27.csv", row.names = FALSE)
rm(myscrape27)

myscrape28 <-  myscrape %>%
  filter(dateMONTH=='2021-07' | dateMONTH=='2021-08')
min(myscrape28$date)
max(myscrape28$date)
write.csv(myscrape28, file="CSV/CC_Scrape_28.csv", row.names = FALSE)
rm(myscrape28)

myscrape29 <-  myscrape %>%
  filter(dateMONTH=='2021-09' | dateMONTH=='2021-10')
min(myscrape29$date)
max(myscrape29$date)
write.csv(myscrape29, file="CSV/CC_Scrape_29.csv", row.names = FALSE)
rm(myscrape29)

myscrape30 <-  myscrape %>%
  filter(dateMONTH=='2021-11' | dateMONTH=='2021-12')
min(myscrape30$date)
max(myscrape30$date)
write.csv(myscrape30, file="CSV/CC_Scrape_30.csv", row.names = FALSE)
rm(myscrape30)
```
- 2022
```{r}
myscrape31 <-  myscrape %>%
  filter(dateMONTH=='2022-01' | dateMONTH=='2022-02')
min(myscrape31$date)
max(myscrape31$date)
write.csv(myscrape31, file="CSV/CC_Scrape_31.csv", row.names = FALSE)
rm(myscrape31)

myscrape32 <-  myscrape %>%
  filter(dateMONTH=='2022-03' | dateMONTH=='2022-04')
min(myscrape32$date)
max(myscrape32$date)
write.csv(myscrape32, file="CSV/CC_Scrape_32.csv", row.names = FALSE)
rm(myscrape32)

myscrape33<-  myscrape %>%
  filter(dateMONTH=='2022-05' | dateMONTH=='2022-06')
min(myscrape9$date)
max(myscrape9$date)
write.csv(myscrape9, file="CSV/CC_Scrape_33.csv", row.names = FALSE)
rm(myscrape33)

myscrape34 <-  myscrape %>%
  filter(dateMONTH=='2022-07' | dateMONTH=='2022-08')
min(myscrape34$date)
max(myscrape34$date)
write.csv(myscrape34, file="CSV/CC_Scrape_34.csv", row.names = FALSE)
rm(myscrape34)
```
3. Load the scraped files post [scrape](https://github.com/nwccpp/climatechange/blob/main/climatechange-article-scrape.py) and join them with master folder
```{r}
path_scraped <- c("CSV/Scraped") # write the path
CC <- list.files(path = path_scraped,  # Identify all CSV files
                       pattern = "*.csv", full.names = TRUE) %>%
  lapply(read_csv) %>%                             
  bind_rows  

CC<- CC %>%
  distinct(master_index,.keep_all = TRUE) %>% # remove any duplicates 
  drop_na(text) # record the number then drop nas
```
4. Run keyword search on the full text
```{r}
###create a list of search words
cc_kw<-c("climate",
         "climate change",
         "climate crisis",
         "climate effects",
         "climate hoax",
         "climate policy",
         "climate resilience",
         "climate science",
         "climate summit",
         "global warming",
         "greenhouse gas",
         "greenhouse gases",
         "ipcc",
         "green energy",
         "climate hypocrisy",
         "paris agreement",
         "paris climate",
         "net zero",
         "net-zero",
         "cop26",
         "climate conversation",
         "climate test",
         "climate gap",
         "climate activists",
         "climate activist",
         "clean energy",
         "climate negotiations",
         "climate deal",
         "green new deal",
         "climate conference",
         "green technology",
         "green tech",
         "climate fearmongering",
         "climate fears",
         "climate anxiety",
         "carbon capture",
         "co2", 
         "climate", 
         "carbon", 
         "methane" ,
         "extreme weather",
         "sea level",
         "sea levels",
         "extreme temperature",
         "extreme temperatures",
         "decarbonization",
         "extreme heat")

cc_kw<-paste(cc_kw, sep = " ", collapse = " | ") # make them into a list with separator for grep
CC$text <- tolower(CC$text) # lower case

CC_filter<- dplyr::filter(CC, grepl(cc_kw, text, ignore.case=TRUE)) # run the filter 
```
5. First delete domains from manual delete list
```{r}
deletedomains <- read_csv("CSV/NW_CC_postfilter_Domains_MBFC_NG_Volumesv2.csv")
todelete <- deletedomains %>% filter(notes == "delete" |
                                   notes == "DELETE")
myCC <- CC_filter %>%
  dplyr:: filter(!url_to_test %in% todelete)
```
6. Now select low credibility sources, NG scores less than 60 and MBFC categories of questionable_sources, conspiracy-pseudocience, and right bias
```{r}
test_cat <- myCC %>% count(category_mbfc_score) # view the categories

myCC_lowcred <-myCC %>%
  filter(between(category_mbfc_score, 1, 60) |
           category_mbfc_score == "questionable_sources" |
           category_mbfc_score == "conspiracy-pseudocience" |
           category_mbfc_score == "right_bias")
test_cat_lowcred <- myCC_lowcred %>% count(category_mbfc_score) # to verify the filter
min(myCC_lowcred$date) # to verify the dates
max(myCC_lowcred$date) # to verify the dates

write.csv(myCC_lowcred, file="CSV/NW_CC_2017_2022_lowcred.csv", row.names = FALSE)
save(myCC_lowcred, file="Rda/NW_CC_2017_2022_lowcred.Rda")
```
7. Split to years for classifier for memory and time
```{r}
myCC_lowcred$year <- lubridate::year(myCC_lowcred$date)

myCC_lowcred %>% count(year)

# 2017
myCC_lowcred_2017 <- myCC_lowcred %>%
  filter(year == '2017')
write.csv(myCC_lowcred_2017, file="CSV/NW_CC_2017_lowcred.csv", row.names=FALSE)

# 2018
myCC_lowcred_2018 <- myCC_lowcred %>%
  filter(year == '2018')
write.csv(myCC_lowcred_2018, file="CSV/NW_CC_2018_lowcred.csv", row.names=FALSE)

# 2019
myCC_lowcred_2019 <- myCC_lowcred %>%
  filter(year == '2019')
write.csv(myCC_lowcred_2019, file="CSV/NW_CC_2019_lowcred.csv", row.names=FALSE)

# 2020
myCC_lowcred_2020 <- myCC_lowcred %>%
  filter(year == '2020')
write.csv(myCC_lowcred_2020, file="CSV/NW_CC_2020_lowcred.csv", row.names=FALSE)

# 2021
myCC_lowcred_2021 <- myCC_lowcred %>%
  filter(year == '2021')
write.csv(myCC_lowcred_2021, file="CSV/NW_CC_2021_lowcred.csv", row.names=FALSE)

# 2022
myCC_lowcred_2022 <- myCC_lowcred %>%
  filter(year == '2022')
write.csv(myCC_lowcred_2022, file="CSV/NW_CC_2022_lowcred.csv", row.names=FALSE)
```

