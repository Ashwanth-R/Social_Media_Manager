# import os
# from textwrap import dedent
# from crewai import Agent
# from tools.browser_tools import BrowserTools
# from tools.search_tools import SearchTools
# from tools.trends_tools import TrendsTools
# from openai_manager import OpenAIManager
# from tools.threads_tools import ThreadsTools
# from tools.instagram_tools import InstagramTools
# from tools.facebook_tools import FacebookTools

# from dotenv import load_dotenv
# load_dotenv()


# class ViralContentCreators:
# 	def __init__(self):
# 		model = os.getenv("MODEL")
# 		if not model:
# 			raise ValueError()
# 		openai_manager = OpenAIManager(model)
# 		self.llm = openai_manager.create_llm()

# 	def trending_topic_researcher_agent(self):
# 		return Agent(
# 			role="Trending Topic Researcher",
# 			goal=dedent("""\
# 				Identify and compile a list of current trending topics and searches
# 				within a specific niche. This list should provide actionable insights
# 				and opportunities for strategic engagement, helping to guide content
# 				creation."""),
# 			backstory=dedent("""\
# 				As a Trending Topic Researcher at a cutting-edge digital
# 				marketing agency, your primary responsibility is to monitor and
# 				decode the pulse of the market. Using advanced analytical tools,
# 				you uncover and list the most relevant trends that can influence
# 				strategic decisions in content creation."""),
# 			tools=[
# 					BrowserTools.scrape_and_summarize_website,
# 					TrendsTools.trending_searches_on_google,
# 					SearchTools.search_internet
# 			],
# 			allow_delegation=False,
# 			llm=self.llm,
# 			verbose=True
# 		)


# 	def content_researcher_agent(self):
# 		return Agent(
# 			role="Content Researcher",
# 			goal=dedent("""\
# 				Conduct in-depth research on a topic and compile
# 				detailed, useful information and insights for each topic. This
# 				information should be actionable and suitable for creating engaging
# 				and informed social media posts. Make it shorter for threads."""),
# 			backstory=dedent("""\
# 				As a Content Researcher at a dynamic social media marketing agency,
# 				you delve deeply into trending topics to uncover underlying themes and
# 				insights. Your ability to discern and utilize authoritative and relevant
# 				sources ensures the content you help create resonates with audiences and
# 				drives engagement."""),
# 			tools=[
# 				BrowserTools.scrape_and_summarize_website,
# 				SearchTools.search_internet,
# 			],
# 			llm=self.llm,
# 			verbose=True
# 		)


# 	def creative_content_creator_agent(self):
# 		return Agent(
# 			role="Social Media Content Creator",
# 			goal=dedent("""\
# 				Develop compelling and innovative content
# 				for social media campaigns, with a focus on creating
# 				high-impact posts for Threads, Instagram, and Facebook. Make sure you don't use tools with the same arguments twice.
# 				Make sure not to do more than 5 google searches. Make it shorter for threads."""),
# 			backstory=dedent("""\
# 				As a Creative Content Creator at a top-tier
# 				digital marketing agency, you excel in crafting narratives
# 				that resonate with audiences on social media.
# 				Your expertise lies in turning marketing strategies
# 				into engaging stories and visual content that capture
# 				attention and inspire action. All three platforms content should not be same make sure of it."""),
# 			tools=[
# 				BrowserTools.scrape_and_summarize_website,
# 				SearchTools.search_internet
# 			],
# 			llm=self.llm,
# 			verbose=True
# 		)

# 	def content_posting_agent(self):
# 		return Agent(
# 			role="Content Posting Agent",
# 			goal=dedent("""\
# 				Post content on Threads, Instagram, and Facebook using the provided tools.
# 				Ensure that each post is correctly formatted and successfully published on the respective platforms.
# 				Ensure each content is posted only once without any retries.
# 				Move to the next platform after successful posting.
# 			   All three platforms content should not be same make sure of it. Make it shorter for threads."""), 
# 			backstory=dedent("""\
# 				As a Content Posting Agent at a leading digital marketing agency, your role is to ensure that
# 				the meticulously crafted content reaches the intended audience on various social media without any
# 				redundant attempts or re-posts.
# 				Your expertise in handling different social media APIs ensures seamless and effective content distribution."""), 
# 			tools=[
# 				ThreadsTools.post_threads,
# 				InstagramTools.post_instagram,
# 				FacebookTools.post_facebook
# 			],
# 			llm=self.llm,
# 			verbose=True
# 		)

import os
from textwrap import dedent
from crewai import Agent
from tools.browser_tools import BrowserTools
from tools.search_tools import SearchTools
from tools.trends_tools import TrendsTools
from openai_manager import OpenAIManager
from tools.threads_tools import ThreadsTools
from tools.instagram_tools import InstagramTools
from tools.facebook_tools import FacebookTools

from dotenv import load_dotenv
load_dotenv()


class ViralContentCreators:
	def __init__(self):
		model = os.getenv("MODEL")
		if not model:
			raise ValueError()
		openai_manager = OpenAIManager(model)
		self.llm = openai_manager.create_llm()

	def trending_topic_researcher_agent(self):
		return Agent(
			role="Trending Topic Researcher",
			goal=dedent("""\
				Identify and compile a curated list of the most relevant and high-impact trending topics within a specific niche. 
			   Provide actionable insights that empower content creators to produce timely and engaging social media content."""),
			backstory=dedent("""\
				As a Trending Topic Researcher at an AI-powered social media marketing agency, 
				your role is to stay ahead of the curve by analyzing real-time trends across the internet. 
				Using advanced research tools and AI-driven insights, you filter through vast amounts of online data to detect emerging conversations, viral discussions, and industry-relevant searches. 
				Your findings serve as the foundation for crafting engaging content that resonates with the target audience and maximizes reach."""),
			tools=[
					BrowserTools.scrape_and_summarize_website,
					TrendsTools.trending_searches_on_google,
					SearchTools.search_internet
			],
			allow_delegation=False,
			llm=self.llm,
			verbose=True
		)


	def content_researcher_agent(self):
		return Agent(
			role="Content Researcher",
			goal=dedent("""\
				Perform in-depth research on selected trending topics, gathering key insights, credible sources, 
			   and valuable context to aid in creating engaging, informative, and high-quality social media content.'
			   Make sure all the platform posts are not redundant and are unique from each posts.
			   Make it shorter for threads."""),
			backstory=dedent("""\
				As a Content Researcher, you are the knowledge hub of the team. 
				You dig deep into each trending topic, extracting meaningful data, fact-checking information, and identifying angles that can drive engagement. 
				With a sharp analytical mindset and a keen eye for credible sources, 
				you ensure that every content piece is well-informed, compelling, and aligned with audience interests. 
				Your work ensures that content creators have the necessary research to craft posts that captivate and educate users.
				"""),
			tools=[
				BrowserTools.scrape_and_summarize_website,
				SearchTools.search_internet,
			],
			llm=self.llm,
			verbose=True
		)


	def creative_content_creator_agent(self):
		return Agent(
			role="Social Media Content Creator",
			goal=dedent("""\
				Transform research insights into compelling, platform-specific content for Threads, Instagram, and Facebook. 
			   Ensure each post is engaging, visually appealing, and uniquely tailored to its respective platform, 
			   avoiding duplication across platforms. 
			   Make sure all the platform posts are not redundant and are unique from each posts.
			   Make it shorter for threads."""),
			backstory=dedent("""\
				As a Creative Content Creator, you are the storyteller of the digital age. 
				Your expertise lies in crafting engaging, high-impact content that speaks directly to the audience. 
				Whether it's a witty Twitter thread, an eye-catching Instagram post, or an informative Facebook update, 
				you shape content to fit the platform's unique audience. 
				With a deep understanding of social media trends and audience engagement strategies, you ensure that every post is optimized for virality and shareability."""),
			tools=[
				BrowserTools.scrape_and_summarize_website,
				SearchTools.search_internet
			],
			llm=self.llm,
			verbose=True
		)

	def content_posting_agent(self):
		return Agent(
			role="Content Posting Agent",
			goal=dedent("""\
				Seamlessly publish content on Threads, Instagram, and Facebook while ensuring correct formatting, proper scheduling, and successful posting. 
			   	Prevent redundant uploads and guarantee smooth content distribution across platforms.
			   Make sure all the platform posts are not redundant and are unique from each posts.
				Make it shorter for threads."""), 
			backstory=dedent("""\
				As a Content Posting Agent, you are the bridge between content creation and audience engagement. 
				You ensure that meticulously crafted content is published flawlessly across multiple social media platforms. 
				With expertise in API handling and automation, you eliminate errors, prevent duplicate posts, and optimize content delivery for maximum impact. 
				Your precision-driven approach ensures that every post reaches the right audience at the right time, maximizing visibility and engagement."""), 
			tools=[
				ThreadsTools.post_threads,
				InstagramTools.post_instagram,
				FacebookTools.post_facebook
			],
			llm=self.llm,
			verbose=True
		)