import uuid
import threading
from enum import Enum
from typing import List , Set
from abc import ABC
from datetime import datetime
from typing import Dict, Optional

class VoteType(Enum):
    UPVOTE="UPVOTE"
    DOWNVOTE="DOWNVOTE"

class EventType(Enum):
    QUESTION_UPVOTED="QUESTION_UPVOTED"
    ANSWER_UPVOTED="ANSWER_UPVOTED"
    QUESTION_DOWNVOTED="QUESTION_DOWNVOTED"
    ANSWER_DOWNVOTED="ANSWER_DOWNVOTED"
    ANSWER_ACCEPTED="ANSWER_ACCEPTED"

class Tag:
    def __init__(self, name:str):
        self.name=name
    
    def get_name(self)->str:
        return self.name
    

# User class
class User:
    def __init__(self, name:str):
        self.id=str(uuid.uuid4())
        self.name=name
        self.reputation=0
        self._lock=threading.Lock()
    
    def get_user_id(self)->str:
        return self.id
    
    def get_user_name(self)->str:
        return self.name
    
    def update_repotation(self, change:int):
        with self._lock:
            self.reputation +=change

    def get_reputation(self)->int:
        with self._lock:
            return self.reputation

 # Observer interface       
class PostObserver:
    def on_post_event(self, event:'Event'):
        pass    

# any event like upvote and downvote
class Event:
    def __init__(self, event_type:EventType, actor:User, target_post='Post'):
        self.event_type=event_type
        self.actor=actor
        self.target_post=target_post

    def get_actor(self)->User:
        return self.actor
    
    def get_target_post(self)->'Post':
        return self.target_post
    
    def get_event_type(self)->EventType:
        return self.event_type


class content(ABC):
    def __init__(self, content_id:str, body:str, author:User)->None:
        self.content_id=content_id
        self.body=body
        self.author=author
        # self.creation_time=datetime.now()

    def get_id(self)->int:
        return self.content_id
    
    def get_body(self)->str:
        return self.body
    
    def get_author(self)->User:
        return self.author

# base class for question and answer
class Post(content):
    def __init__(self, post_id:int, body:str, author:User):
        super().__init__(post_id, body, author)
        self.vote_count=0
        self._lock=threading.Lock()
        self.voters: Dict[str, VoteType]={}
        self.observers: List['PostObserver']=[]
        self.comments: List['Comment']=[]

    def add_observers(self, observer:PostObserver):
        self.observers.append(observer)

    def notify_all(self, event:Event):
        for observer in self.observers:
            observer.on_post_event(event)

    def get_vote_count(self)->int:
        with self._lock:
            return self.vote_count
        
    def vote(self, user:User, vote_type:VoteType):
        with self._lock:
            user_id=user.get_user_id()
            vote_change=0
            if user_id in self.voters:
                if self.voters.get(user_id)==vote_type:
                    return
                if vote_type==VoteType.UPVOTE:
                    vote_change +=2
                else:
                    vote_change -=2
            else:
                if vote_type==VoteType.UPVOTE:
                    vote_change +=1
                else:
                    vote_change -=1
            self.vote_count+=vote_change

            if isinstance(self,Question):
                if vote_type==VoteType.UPVOTE:
                    event_type=EventType.QUESTION_UPVOTED
                else:
                    event_type=EventType.QUESTION_DOWNVOTED
            else:
                if vote_type==VoteType.UPVOTE:
                    event_type=EventType.ANSWER_UPVOTED
                else:
                    event_type=EventType.ANSWER_DOWNVOTED
            self.notify_all(Event(event_type, user, self))

    def get_comments(self)->List['Comment']:
        return self.comments
    
    def add_comments(self, comment:'Comment'):
        self.comments.append(comment)

class Comment(Post):
    def __init__(self, body:str, author:User):
        super().__init__(str(uuid.uuid4()), body, author)
        self.body=body
        self.author=author
        self.creation_time=datetime.now()
             
class Answer(Post):
    def __init__(self, body:str, author:User):
        super().__init__(str(uuid.uuid4()), body, author)
        self.is_accepted=False

    def is_answer_accepted(self)->bool:
        return self.is_accepted
    
    def set_accepted(self, accepted:bool):
        self.is_accepted=accepted

class Question(Post):
    def __init__(self, body:str, author:User, title:str, tags:Set['Tag']):
        super().__init__(str(uuid.uuid4()), body, author)
        self._lock=threading.Lock()
        self.title=title
        self.tags: List['Tag']=tags
        self.answers:List['Answer']=[]
        self.accepted_answer: Optional['Answer'] =None

    def get_title(self)->str:
        return self.title
    
    def get_tags(self)->List['Tag']:
        return self.tags

    def get_answers(self)->List['Answer']:
        return self.answers
    
    def add_answer(self, answer:Answer):
        self.answers.append(answer)
    
    def set_accepted_answer(self, answer:'Answer'):
        with self._lock:
            if answer.get_author().get_user_id() != self.get_author().get_user_id():
                if self.accepted_answer is None:
                    self.accepted_answer=answer
                    answer.set_accepted(True)
                    self.notify_all(Event(EventType.ANSWER_ACCEPTED, self.get_author(), answer))

    def get_accepted_answer(self)->Optional['Answer']:
        return self.accepted_answer

# obersver to manage reputation
class ReputationManager(PostObserver):
    QUESTION_UPVOTE_REP = 5
    ANSWER_UPVOTE_REP = 10
    ACCEPTED_ANSWER_REP = 15
    DOWNVOTE_REP_PENALTY = -1  # Penalty for the voter
    POST_DOWNVOTED_REP_PENALTY = -2  # Penalty for the post author

    def on_post_event(self, event):
        author=event.get_target_post().get_author()
        event_type=event.get_event_type()

        if event_type==EventType.QUESTION_UPVOTED:
            author.update_repotation(self.QUESTION_UPVOTE_REP)
        elif event_type==EventType.ANSWER_UPVOTED:
            author.update_repotation(self.ANSWER_UPVOTE_REP)
        elif event_type==EventType.ANSWER_ACCEPTED:
            author.update_repotation(self.ACCEPTED_ANSWER_REP)
        elif event_type==EventType.QUESTION_DOWNVOTED or event_type==EventType.ANSWER_DOWNVOTED:
            author.update_repotation(self.POST_DOWNVOTED_REP_PENALTY)
            voter=event.get_actor()
            voter.update_repotation(self.DOWNVOTE_REP_PENALTY)

# strategy pattern for searching questions
class SearchStrategy:
    def filters(self, questions : List['Question']) -> List['Question']:
        pass
# concrete strategy 1
class KeywordSearchStrategy(SearchStrategy):
    def __init__(self, keyword:str):
        self.keyword=keyword.lower()

    def filters(self, questions : List['Question']) -> List['Question']:
        return [q for q in questions if self.keyword in q.title.lower() or self.keyword in q.get_body().lower()]
# concrete strategy 2
class TagSearchStrategy(SearchStrategy):
    def __init__(self, tag: Tag):
        self.tag=tag

    def filters(self, questions : List['Question']) -> List['Question']:
        return [q for q in questions if (t.get_name().lower() == self.tag.get_name().lower() for t in q.get_tags())]
# concrete strategy 3
class UserSearchStrategy(SearchStrategy):
    def __init__(self, user: User):
        self.user=user

    def filters(self, questions : List['Question']) -> List['Question']:
        return [q for q in questions if q.get_author().get_user_id() == self.user.get_user_id()]

# Facade for StackOverflow service
class StackOverflowService:
    def __init__(self):
        self.users: Dict[str, User]={}
        self.questions: Dict[int, Question]={}
        self.answers: Dict[int, Answer]={}
        self.reputation_manager=ReputationManager()

    def register_user(self, name:str)->User:
        user=User(name)
        self.users[user.get_user_id()]=user
        return user
    
    def post_question(self, user_id:str, title:str, body:str, tags:Set['Tag'])->Question:
        author=self.users.get(user_id)
        question=Question(body, author, title, tags)
        question.add_observers(self.reputation_manager)
        self.questions[question.get_id()]=question
        return question
    
    def post_answer(self, user_id:str, question_id:int, body:str)->Answer:
        author=self.users.get(user_id)
        question=self.questions.get(question_id)
        answer=Answer(body, author)
        answer.add_observers(self.reputation_manager)
        question.add_answer(answer)
        self.answers[answer.get_id()]=answer
        return answer
    
    def vote_on_post(self, user_id:str, post_id:int, vote_type:VoteType):
        user=self.users.get(user_id)
        post=self.questions.get(post_id) or self.answers.get(post_id)
        post.vote(user, vote_type)

    def accept_answer(self, question_id:int, answer_id:int):
        question=self.questions.get(question_id)
        answer=self.answers.get(answer_id)
        question.set_accepted_answer(answer)

    def search_questions(self, strategies:List[SearchStrategy])->List['Question']:
        results = list(self.questions.values())

        for strategy in strategies:
            results = strategy.filters(results)

        return results
    
    def get_user(self, user_id:str)->User:
        return self.users.get(user_id)
    
    def find_post_by_id(self, post_id:str)->Post:
        if post_id in self.questions:
            return self.questions[post_id]
        elif post_id in self.answers:
            return self.answers[post_id]
        
        raise KeyError("Post not found")
    
class stackOverflowDemo:
    @staticmethod
    def main():
        service=StackOverflowService()

        # 1. Create Users
        alice=service.register_user("Alice")
        bob=service.register_user("Bob")
        charlie=service.register_user("Charlie")
        stackOverflowDemo.print_reputations(alice, bob, charlie)

        # 2. Alice posts a question
        print("--- Alice posts a question ---")
        question1=service.post_question(alice.get_user_id(), "What is Python?", "I want to know about Python programming language.", {Tag("programming"), Tag("python")})

        # 3. Bob and Charlie post answers
        print("\n--- Bob and Charlie post answers ---")
        answer_bob=service.post_answer(bob.get_user_id(), question1.get_id(), "Python is a high-level programming language.")
        answer_charlie=service.post_answer(charlie.get_user_id(), question1.get_id(), "Python is great for data science.")
        stackOverflowDemo.print_reputations(alice, bob, charlie)


        # 4. Voting happens
        print("\n--- Voting Occurs ---")
        service.vote_on_post(charlie.get_user_id(), question1.get_id(), VoteType.UPVOTE)
        service.vote_on_post(alice.get_user_id(), answer_bob.get_id(), VoteType.UPVOTE)
        service.vote_on_post(alice.get_user_id(), answer_charlie.get_id(), VoteType.UPVOTE)
        stackOverflowDemo.print_reputations(alice, bob, charlie)

        # 5. Alice accepts Charlie's answer
        print("\n--- Alice accepts Charlie's answer ---")
        service.accept_answer(question1.get_id(), answer_bob.get_id())
        stackOverflowDemo.print_reputations(alice, bob, charlie)

        filters_c = [
            UserSearchStrategy(alice),
            TagSearchStrategy({Tag("python")})
        ]
        search_results = service.search_questions(filters_c)
        for q in search_results:
            print(f"  - Found: {q.get_title()}")

    @staticmethod
    def print_reputations(*users):
        print("--- Current Reputations ---")
        for user in users:
            print(f"{user.get_user_name()}: {user.get_reputation()}")


if __name__ == "__main__":
    stackOverflowDemo.main()
