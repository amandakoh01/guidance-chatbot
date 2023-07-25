import { IconClearAll } from '@tabler/icons-react';
import {
  MutableRefObject,
  memo,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';

import { useTranslation } from 'next-i18next';

import {
  saveConversation,
  saveConversations,
  updateConversation,
} from '@/utils/app/conversation';
import { throttle } from '@/utils/data/throttle';

import { Conversation, Message } from '@/types/chat';
import { Plugin } from '@/types/plugin';

import HomeContext from '@/pages/api/home/home.context';

import { ChatInput } from './ChatInput';
import { ChatLoader } from './ChatLoader';
import { MemoizedChatMessage } from './MemoizedChatMessage';

import EventSource from 'eventsource'

interface Props {
  stopConversationRef: MutableRefObject<boolean>;
}

export const Chat = memo(({ stopConversationRef }: Props) => {
  const { t } = useTranslation('chat');

  const {
    state: {
      selectedConversation,
      conversations,
      apiKey,
      pluginKeys,
      loading,
    },
    handleUpdateConversation,
    dispatch: homeDispatch,
  } = useContext(HomeContext);

  const [currentMessage, setCurrentMessage] = useState<Message>();
  const [autoScrollEnabled, setAutoScrollEnabled] = useState<boolean>(true);
  const [showScrollDownButton, setShowScrollDownButton] =
    useState<boolean>(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = useCallback(
    async (message: Message, deleteCount = 0, plugin: Plugin | null = null) => {
      console.log("handle send");

      if (selectedConversation) {
        let updatedConversation: Conversation;
        if (deleteCount) {
          const updatedMessages = [...selectedConversation.messages];
          for (let i = 0; i < deleteCount; i++) {
            updatedMessages.pop();
          }
          updatedConversation = {
            ...selectedConversation,
            messages: [...updatedMessages, message],
          };
        } else {
          updatedConversation = {
            ...selectedConversation,
            messages: [...selectedConversation.messages, message],
          };
        }
        homeDispatch({
          field: 'selectedConversation',
          value: updatedConversation,
        });
        homeDispatch({ field: 'loading', value: true });
        homeDispatch({ field: 'messageIsStreaming', value: true });

        // save this with a conversation name
        if (updatedConversation.messages.length === 1) {
          const { content } = message;
          const customName =
            content.length > 30 ? content.substring(0, 30) + '...' : content;
          updatedConversation = {
            ...updatedConversation,
            name: customName,
          };
        }

        // make http request
        const endpoint = 'http://localhost:8000/chat';

        const url = new URL(endpoint);
        url.searchParams.append('messages', JSON.stringify(updatedConversation.messages));

        console.log(url.toString());

        const eventSource = new EventSource(url.toString());
        
        let isFirst = true;
        let text = '';
        let thoughts = '';
        let isDone = false;
        homeDispatch({ field: 'thoughts', value: thoughts });

        // when done generating or error occurs (save conversation)
        const doneGenerating = () => {
          isDone = true;

          saveConversation(updatedConversation);
          const updatedConversations: Conversation[] = conversations.map(
            (conversation) => {
              if (conversation.id === selectedConversation.id) {
                return updatedConversation;
              }
              return conversation;
            },
          );
          if (updatedConversations.length === 0) {
            updatedConversations.push(updatedConversation);
          }
          homeDispatch({ field: 'conversations', value: updatedConversations });
          saveConversations(updatedConversations);
          homeDispatch({ field: 'messageIsStreaming', value: false });
        };

        // continuously check if generation should be stopped using timer that calls itself
        const checkStopGeneration = () => {
          if (stopConversationRef.current === true) {
            eventSource.close();

            if (isFirst) {
              homeDispatch({ field: 'loading', value: false });
              isFirst = false;
              const updatedMessages: Message[] = [
                ...updatedConversation.messages,
                { role: 'assistant', content: "User stopped generation"},
              ];
              updatedConversation = {
                ...updatedConversation,
                messages: updatedMessages,
              };
              console.log(updatedConversation);
              homeDispatch({
                field: 'selectedConversation',
                value: updatedConversation,
              });
            }
            doneGenerating();
          } else if (!isDone) {
            setTimeout(() => {
              checkStopGeneration();
            }, 1000);
          }
        }

        // run function above
        checkStopGeneration();

        // error listener: close event source and alert
        eventSource.addEventListener('error', function() {
          if (isDone) return;

          eventSource.close();

          alert("Unable to connect to the server");

          // add "error contacting server" as a message if nothing came through yet
          if (isFirst) {
            homeDispatch({ field: 'loading', value: false });
            isFirst = false;
            const updatedMessages: Message[] = [
              ...updatedConversation.messages,
              { role: 'assistant', content: "Error contacting server"},
            ];
            updatedConversation = {
              ...updatedConversation,
              messages: updatedMessages,
            };
            console.log(updatedConversation);
            homeDispatch({
              field: 'selectedConversation',
              value: updatedConversation,
            });
          }
          doneGenerating();
        }
        )

        eventSource.addEventListener('open', function() {
          console.log("connection open");
        })

        // stream listener (add to sidebar - by dispatching to home)
        eventSource.addEventListener('stream', function(event) {
          thoughts += event.data;
          homeDispatch({ field: 'thoughts', value: thoughts });

          console.log(`stream: '${event.data}'`);
        })

        // final answer listener (adds to both sidebar & main message)
        eventSource.addEventListener('final', function(event) {
          // continue streaming
          thoughts += event.data;
          homeDispatch({ field: 'thoughts', value: thoughts });

          console.log(`final answer: '${event.data}'`);

          text += event.data;
          if (isFirst) {
            homeDispatch({ field: 'loading', value: false });
            isFirst = false;
            const updatedMessages: Message[] = [
              ...updatedConversation.messages,
              { role: 'assistant', content: event.data},
            ];
            updatedConversation = {
              ...updatedConversation,
              messages: updatedMessages,
            };
            console.log(updatedConversation);
            homeDispatch({
              field: 'selectedConversation',
              value: updatedConversation,
            });
          } else {
            // otherwise, add it to the last one
            const updatedMessages: Message[] =
              updatedConversation.messages.map((message, index) => {
                if (index === updatedConversation.messages.length - 1) {
                  return {
                    ...message,
                    content: text,
                  };
                }
                return message;
              });
            updatedConversation = {
              ...updatedConversation,
              messages: updatedMessages,
            };
            homeDispatch({
              field: 'selectedConversation',
              value: updatedConversation,
            });
          }
        })

        // done event listener (ends stream and calls the done generating function which saves the convo)
        eventSource.addEventListener('done', function(event) {
          console.log("stream over!!");
          eventSource.close();
          doneGenerating();
        })
      }
    },
    [
      apiKey,
      conversations,
      pluginKeys,
      selectedConversation,
      stopConversationRef,
    ],
  );

  const scrollToBottom = useCallback(() => {
    if (autoScrollEnabled) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      textareaRef.current?.focus();
    }
  }, [autoScrollEnabled]);

  const handleScroll = () => {
    if (chatContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } =
        chatContainerRef.current;
      const bottomTolerance = 30;

      if (scrollTop + clientHeight < scrollHeight - bottomTolerance) {
        setAutoScrollEnabled(false);
        setShowScrollDownButton(true);
      } else {
        setAutoScrollEnabled(true);
        setShowScrollDownButton(false);
      }
    }
  };

  const handleScrollDown = () => {
    chatContainerRef.current?.scrollTo({
      top: chatContainerRef.current.scrollHeight,
      behavior: 'smooth',
    });
  };

  const onClearAll = () => {
    if (
      confirm(t<string>('Are you sure you want to clear all messages?')) &&
      selectedConversation
    ) {
      handleUpdateConversation(selectedConversation, {
        key: 'messages',
        value: [],
      });
    }
  };

  const scrollDown = () => {
    if (autoScrollEnabled) {
      messagesEndRef.current?.scrollIntoView(true);
    }
  };
  const throttledScrollDown = throttle(scrollDown, 250);

  useEffect(() => {
    throttledScrollDown();
    selectedConversation &&
      setCurrentMessage(
        selectedConversation.messages[selectedConversation.messages.length - 2],
      );
  }, [selectedConversation, throttledScrollDown]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        setAutoScrollEnabled(entry.isIntersecting);
        if (entry.isIntersecting) {
          textareaRef.current?.focus();
        }
      },
      {
        root: null,
        threshold: 0.5,
      },
    );
    const messagesEndElement = messagesEndRef.current;
    if (messagesEndElement) {
      observer.observe(messagesEndElement);
    }
    return () => {
      if (messagesEndElement) {
        observer.unobserve(messagesEndElement);
      }
    };
  }, [messagesEndRef]);

  return (
    <div className="relative flex-1 overflow-hidden bg-white dark:bg-[#343541]">
      <>
        <div
          className="max-h-full overflow-x-hidden"
          ref={chatContainerRef}
          onScroll={handleScroll}
        >
          {selectedConversation?.messages.length === 0 ? (
            <>
              <div className="mx-auto flex flex-col space-y-5 md:space-y-10 px-3 pt-5 md:pt-12 sm:max-w-[600px]">
                <div className="text-center text-3xl font-semibold text-gray-800 dark:text-gray-100">
                  COCO v2
                </div>
              </div>
            </>
          ) : (
            <>
              <div className="sticky top-0 z-10 flex justify-center border border-b-neutral-300 bg-neutral-100 py-2 text-sm text-neutral-500 dark:border-none dark:bg-[#444654] dark:text-neutral-200">
                Current conversation: {selectedConversation?.name} | 
                <button
                  className="ml-2 cursor-pointer hover:opacity-50"
                  onClick={onClearAll}
                >
                  <IconClearAll size={18} />
                </button>
              </div>
              {selectedConversation?.messages.map((message, index) => (
                <MemoizedChatMessage
                  key={index}
                  message={message}
                  messageIndex={index}
                  onEdit={(editedMessage) => {
                    setCurrentMessage(editedMessage);
                    // discard edited message and the ones that come after then resend
                    handleSend(
                      editedMessage,
                      selectedConversation?.messages.length - index,
                    );
                  }}
                />
              ))}

              {loading && <ChatLoader />}

              <div
                className="h-[162px] bg-white dark:bg-[#343541]"
                ref={messagesEndRef}
              />
            </>
          )}
        </div>

        <ChatInput
          stopConversationRef={stopConversationRef}
          textareaRef={textareaRef}
          onSend={(message, plugin) => {
            setCurrentMessage(message);
            handleSend(message, 0, plugin);
          }}
          onScrollDownClick={handleScrollDown}
          onRegenerate={() => {
            if (currentMessage) {
              handleSend(currentMessage, 2, null);
            }
          }}
          showScrollDownButton={showScrollDownButton}
        />
      </>
    </div>
  );
});
Chat.displayName = 'Chat';
