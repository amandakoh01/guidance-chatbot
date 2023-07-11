import { IconBrain, IconClearAll } from '@tabler/icons-react';
import { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';

import { useContext, useEffect, useState } from 'react';

import HomeContext from '@/pages/api/home/home.context';

import { MemoizedReactMarkdown } from '../Markdown/MemoizedReactMarkdown';

import {
  CloseSidebarButton,
  OpenSidebarButton,
} from './components/OpenCloseButton';

const Thoughtbar = () => {

    const {
        state: { showPromptbar, thoughts },
        dispatch: homeDispatch,
    } = useContext(HomeContext);

    const handleTogglePromptbar = () => {
        homeDispatch({ field: 'showPromptbar', value: !showPromptbar });
        localStorage.setItem('showPromptbar', JSON.stringify(!showPromptbar));
    };

    const clearThoughts = () => {
        homeDispatch({ field: 'thoughts', value: "" });
    }

    return showPromptbar ? (
        <div>
            <div
            className={`fixed top-0 $right-0 z-40 flex-row h-full w-[260px] flex-row space-y-2 bg-[#202123] p-2 text-[14px] transition-all sm:relative sm:top-0`}
            >
                <div className="flow-root w-full">
                    <div className="float-left">
                        <div className="text-sidebar flex items-center gap-3 p-3 text-white">
                            <IconBrain size={16} />
                            Thoughts
                        </div>
                    </div>

                    <div className="float-right">
                        <button
                            className="ml-2 cursor-pointer items-center rounded-md border border-white/20 p-3 text-sm text-white transition-colors duration-200 hover:bg-gray-500/10"
                        >
                            <IconClearAll size={16} onClick={clearThoughts}/>
                        </button>
                    </div>
                </div>
                    
                <div className="text-sidebar flex flex-col items-left gap-3 p-3 text-white">
                    <MemoizedReactMarkdown>{thoughts}</MemoizedReactMarkdown>
                </div>
                
            </div>

            <CloseSidebarButton onClick={handleTogglePromptbar} side='right' />
        </div>
    ) : (
        <OpenSidebarButton onClick={handleTogglePromptbar} side='right' />
    );
};

export default Thoughtbar;
