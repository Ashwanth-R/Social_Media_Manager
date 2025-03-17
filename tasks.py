# from crewai import Task
# from textwrap import dedent

# class ViralContentCreationTasks:
#     def topic_analysis(self, agent, niche):
#         return Task(
#             description=dedent(f"""\
#                 Find trending searches/topics related to the niche:{niche}, in the past 10 days.
                
#                 Compile this information into a structured list of topics and searches. 
#                 Each item in the list should include a brief description and relevance score 
#                 to guide content creation efforts around these trends. 
#                 Ensure the final list of trending topics is clear, actionable, and ready to inform strategic 
#                 content development."""),
#             expected_output="List of trending topics and searches in the format: [topic1, topic2, ...]",
#             agent=agent
#         )

#     def content_research(self, agent, niche):
#         return Task(
#             description=dedent(f"""\
#                 Do in-depth research of all the trending topics and searches.
#                 For each trending topic related to - {niche}, search for 
#                     the most authoritative and relevant websites within the {niche} niche.
#                     Create a list of websites to visit for each trending topic.
                    
#                     Compile comprehensive details for each topic, including:
#                         - A summary of the topic's significance.
#                         - Statistical data or recent studies related to the topic.
#                         - Current discussion points or controversies.
#                         - Predictions or trends that indicate how this topic might evolve.
#                         - Possible angles or hooks for content creation.
                        
#                     Maximum number of google searches you can do is 5."""),
#             expected_output=dedent(f"""\
#                           A map of trending topic to structured research details for that topic.
#                         This report will serve as a foundation 
#                         for creating targeted, informed, and engaging social media posts"""),
#             agent=agent
#         )

#     def create_social_media_posts(self, agent, niche):
#         return Task(
#             description=dedent(f"""\
#                 First filter out the topics that are related to {niche} and remove the ones not related.
#                 Next, create 1 post each for Threads, Instagram, and Facebook using the content research done for each of 
#                     the trending topics/searches and craft engaging, valuable, and actionable posts that are ready to 
#                     be published. Try to use the following structure:
#                     1. Start with a Strong Hook: Begin with an intriguing question, startling fact, or 
#                             engaging statement to grab attention.
#                     2. Add Value or Insight: Incorporate useful and relevant information such as statistics, 
#                             quick tips, or enlightening observations or interesting facts.
#                     3. Call to Action (CTA): Encourage readers to engage further by trying out a tip, 
#                             sharing the post, or leaving comments. And give them some useful relevant link to
#                             blog, website, or video.
#                     4. Use Appropriate Hashtags: Include 2-3 relevant hashtags to enhance visibility 
#                             but avoid overuse.

#                     Example Post:
#                     "Did you know that 10 minutes of meditation daily can boost your focus significantly? 
#                         🧘‍♂️✨ Consistent, brief meditation improves concentration and stress levels, even during work hours. 
#                         It's not just good for your mind—it's a productivity booster!
#                         Give it a try tomorrow morning, and see the difference for yourself! 
#                         🌞🚀 Share this tip with someone who needs a focus boost. 
#                         #ProductivityHacks #Mindfulness #MentalHealth"

#                 Note: Ensure each post is standalone and provides all necessary context, as users might 
#                       not see other related posts. Compile these posts into a document or list, with each entry clearly 
#                       labeled with the topic it addresses. This document will be used by another agent to handle 
#                       the actual posting on social media.
                      
#                 After executing this task, you should print the output.
#                 Task should return an array containing all the posts for Twitter, Instagram, and Facebook in the format: 
#                 [threads_post, instagram_post, facebook_post]"""),
#             expected_output="Array containing all the social media posts in the format: [threads_post, instagram_post, facebook_post]",
#             agent=agent
#         )

#     def post_content(self, agent):
#         return Task(
#             description=dedent("""\
#                 Post the generated content on Threads, Instagram, and Facebook.
#                 Ensure that each post is correctly formatted and successfully published on the respective platforms."""), 
#             expected_output="Confirmation of successful posting on all platforms.",
#             agent=agent
#         )


from crewai import Task
from textwrap import dedent

class ViralContentCreationTasks:
    def topic_analysis(self, agent, niche):
        return Task(
            description=dedent(f"""\
                Identify trending topics related to the niche: {niche} by analyzing search trends, social media discussions, 
                and news sources from the past 10 days. 

                Compile a structured list of relevant topics, ensuring each entry includes:
                - A brief summary of why it is trending.
                - Its potential engagement level (high, medium, or low).
                - Any relevant hashtags or keywords associated with it.
                
                This task will help in guiding content creation to align with ongoing trends and maximize audience reach."""),
            expected_output="A structured list of trending topics with summaries, engagement levels, and relevant hashtags.",
            agent=agent
        )

    def content_research(self, agent, niche):
        return Task(
            description=dedent(f"""\
                Perform in-depth research on each trending topic identified for the niche: {niche}. 

                For each topic:
                - Extract key details such as its significance, recent statistics, and expert opinions.
                - Identify emerging trends, discussions, and potential controversies.
                - Gather insights from authoritative sources such as research articles, news reports, and popular blogs.
                - Suggest different content angles or perspectives that can make posts more engaging.

                Ensure all insights are structured and easily usable for content creation.
                Maximum number of Google searches allowed: 5."""),
            expected_output="A well-structured research document mapping each topic to its insights, stats, and content ideas.",
            agent=agent
        )

    def create_social_media_posts(self, agent, niche):
        return Task(
            description=dedent(f"""\
                Generate engaging social media posts for Threads, Instagram, and Facebook using the researched trending topics in {niche}. 

                For each platform:
                - Adapt the post style to fit the audience and engagement patterns of that platform.
                - Ensure content is unique for each platform (not copy-pasted across all).
                - Structure each post with:
                    1. *A Strong Hook*: Start with a question, interesting fact, or bold statement.
                    2. *Valuable Insights*: Provide useful information, statistics, or thought-provoking ideas.
                    3. *Call to Action (CTA)*: Encourage likes, comments, shares, or external actions (e.g., visiting a blog or video).
                    4. *Relevant Hashtags*: Use platform-optimized hashtags to increase reach.

                Deliver posts in an array format for easy access by the posting agent.
                Format: [threads_post, instagram_post, facebook_post]."""),
            expected_output="An array containing well-structured posts for Threads, Instagram, and Facebook.",
            agent=agent
        )

    def post_content(self, agent):
        return Task(
            description=dedent("""\
                Publish the generated social media content on Threads, Instagram, and Facebook using automation tools.

                - Ensure that each post is correctly formatted for the respective platform.
                - Avoid duplicate or redundant postings.
                - Verify successful publishing on each platform before moving to the next.
                - Provide a confirmation log indicating successful posts.

                This task ensures seamless and automated content distribution across platforms."""),
            expected_output="A confirmation log verifying successful post submissions on all platforms.",
            agent=agent
        )