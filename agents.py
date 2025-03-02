import os
from textwrap import dedent
from crewai import Agent
from tools.browser_tools import BrowserTools
from tools.search_tools import SearchTools
from tools.trends_tools import TrendsTools
from openai_manager import OpenAIManager
from tools.twitter_tools import TwitterTools
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
				Identify and compile a list of current trending topics and searches
				within a specific niche. This list should provide actionable insights
				and opportunities for strategic engagement, helping to guide content
				creation."""),
			backstory=dedent("""\
				As a Trending Topic Researcher at a cutting-edge digital
				marketing agency, your primary responsibility is to monitor and
				decode the pulse of the market. Using advanced analytical tools,
				you uncover and list the most relevant trends that can influence
				strategic decisions in content creation."""),
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
				Conduct in-depth research on a topic and compile
				detailed, useful information and insights for each topic. This
				information should be actionable and suitable for creating engaging
				and informed social media posts."""),
			backstory=dedent("""\
				As a Content Researcher at a dynamic social media marketing agency,
				you delve deeply into trending topics to uncover underlying themes and
				insights. Your ability to discern and utilize authoritative and relevant
				sources ensures the content you help create resonates with audiences and
				drives engagement."""),
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
				Develop compelling and innovative content
				for social media campaigns, with a focus on creating
				high-impact posts for Twitter, Instagram, and Facebook. Make sure you don't use tools with the same arguments twice.
				Make sure not to do more than 5 google searches."""),
			backstory=dedent("""\
				As a Creative Content Creator at a top-tier
				digital marketing agency, you excel in crafting narratives
				that resonate with audiences on social media.
				Your expertise lies in turning marketing strategies
				into engaging stories and visual content that capture
				attention and inspire action."""),
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
				Post content on Twitter, Instagram, and Facebook using the provided tools.
				Ensure that each post is correctly formatted and successfully published on the respective platforms."""), 
			backstory=dedent("""\
				As a Content Posting Agent at a leading digital marketing agency, your role is to ensure that
				the meticulously crafted content reaches the intended audience on various social media platforms.
				Your expertise in handling different social media APIs ensures seamless and effective content distribution."""), 
			tools=[
				TwitterTools.post_tweet,
				InstagramTools.post_instagram,
				FacebookTools.post_facebook
			],
			llm=self.llm,
			verbose=True
		)