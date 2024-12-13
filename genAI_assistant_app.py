from flask import Flask, render_template_string, request, jsonify
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
import torch
import json
from langdetect import detect, LangDetectException

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <!-- Bootstrap CSS -->
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<style>
    .white-image {
  filter: brightness(0) invert(1); /* Makes the image solid white */
}

.selected {
  background-color: #d55a90 !important;
}

.category-badge {
  border-radius: 24px;
  min-width: 120px;
  min-height: 30px;
  text-transform: capitalize;
  display: inline-block;
  text-align: center;
  vertical-align: middle;
  line-height: 1.5; /* Adjust as per badge size */
  background-color: rgba(var(--bd-violet-rgb), 1) !important;
}

.category-badge-tag {
  border-radius: 24px;
  text-transform: capitalize;
  display: inline-block;
  text-align: center;
  vertical-align: middle;
  line-height: 1.5; /* Adjust as per badge size */
  /* background-image: linear-gradient(
    rgba(var(--bd-violet-rgb), 1),
    rgba(var(--bd-violet-rgb), 0.95)
  ); */
}

.category-badge:hover {
  background-color: #66b2ff; /* Lighter color on hover */
  cursor: pointer; /* Change to pointer on hover */
}

.subcategory-badge {
  border-radius: 18px;
  min-width: 120px;
  min-height: 30px;
  text-transform: capitalize;
  display: inline-block;
  text-align: center;
  vertical-align: middle;
  line-height: 1.5; /* Adjust as per badge size */
  /* background-color: #fbe2ab !important; */
}
.subcategory-badge {
  cursor: pointer; /* Change to pointer on hover */
}

.counter-badge {
  font-size: 11px;
  border-radius: 4px;
}

.ar-ctn-btn {
  border-radius: 20px;
}

.card-title {
  font-size: 1.1rem !important;
  color: white !important;
}

.ai-icon {
  height: 20px;
}

.form-check-input {
  clear: left;
}

.form-switch.form-switch-lg {
  /*margin-bottom: 1 rem;  JUST FOR STYLING PURPOSE */
}

.form-switch.form-switch-lg .form-check-input {
  height: 1.7rem;
  width: calc(3rem + 0.75rem);
  border-radius: 4rem;
}

.form-check-input:checked {
  background-color: #ffc107; /* Bootstrap warning yellow */
  border-color: #ffc107; /* Match border color */
}

</style>
<style>
    /**
 * Skipped minification because the original files appears to be already minified.
 * Original file: /npm/@docsearch/css@3.6.1/dist/style.css
 *
 * Do NOT use SRI with dynamically generated files! More information: https://www.jsdelivr.com/using-sri-with-dynamic-files
 */
/*! @docsearch/css 3.6.1 | MIT License | © Algolia, Inc. and contributors | https://docsearch.algolia.com */
:root {
    --docsearch-primary-color: #5468ff;
    --docsearch-text-color: #1c1e21;
    --docsearch-spacing: 12px;
    --docsearch-icon-stroke-width: 1.4;
    --docsearch-highlight-color: var(--docsearch-primary-color);
    --docsearch-muted-color: #969faf;
    --docsearch-container-background: rgba(101,108,133,0.8);
    --docsearch-logo-color: #5468ff;
    --docsearch-modal-width: 560px;
    --docsearch-modal-height: 600px;
    --docsearch-modal-background: #f5f6f7;
    --docsearch-modal-shadow: inset 1px 1px 0 0 hsla(0,0%,100%,0.5),0 3px 8px 0 #555a64;
    --docsearch-searchbox-height: 56px;
    --docsearch-searchbox-background: #ebedf0;
    --docsearch-searchbox-focus-background: #fff;
    --docsearch-searchbox-shadow: inset 0 0 0 2px var(--docsearch-primary-color);
    --docsearch-hit-height: 56px;
    --docsearch-hit-color: #444950;
    --docsearch-hit-active-color: #fff;
    --docsearch-hit-background: #fff;
    --docsearch-hit-shadow: 0 1px 3px 0 #d4d9e1;
    --docsearch-key-gradient: linear-gradient(-225deg,#d5dbe4,#f8f8f8);
    --docsearch-key-shadow: inset 0 -2px 0 0 #cdcde6,inset 0 0 1px 1px #fff,0 1px 2px 1px rgba(30,35,90,0.4);
    --docsearch-key-pressed-shadow: inset 0 -2px 0 0 #cdcde6,inset 0 0 1px 1px #fff,0 1px 1px 0 rgba(30,35,90,0.4);
    --docsearch-footer-height: 44px;
    --docsearch-footer-background: #fff;
    --docsearch-footer-shadow: 0 -1px 0 0 #e0e3e8,0 -3px 6px 0 rgba(69,98,155,0.12)
}

html[data-theme=dark] {
    --docsearch-text-color: #f5f6f7;
    --docsearch-container-background: rgba(9,10,17,0.8);
    --docsearch-modal-background: #15172a;
    --docsearch-modal-shadow: inset 1px 1px 0 0 #2c2e40,0 3px 8px 0 #000309;
    --docsearch-searchbox-background: #090a11;
    --docsearch-searchbox-focus-background: #000;
    --docsearch-hit-color: #bec3c9;
    --docsearch-hit-shadow: none;
    --docsearch-hit-background: #090a11;
    --docsearch-key-gradient: linear-gradient(-26.5deg,#565872,#31355b);
    --docsearch-key-shadow: inset 0 -2px 0 0 #282d55,inset 0 0 1px 1px #51577d,0 2px 2px 0 rgba(3,4,9,0.3);
    --docsearch-key-pressed-shadow: inset 0 -2px 0 0 #282d55,inset 0 0 1px 1px #51577d,0 1px 1px 0 rgba(3,4,9,0.30196078431372547);
    --docsearch-footer-background: #1e2136;
    --docsearch-footer-shadow: inset 0 1px 0 0 rgba(73,76,106,0.5),0 -4px 8px 0 rgba(0,0,0,0.2);
    --docsearch-logo-color: #fff;
    --docsearch-muted-color: #7f8497
}

.DocSearch-Button {
    align-items: center;
    background: var(--docsearch-searchbox-background);
    border: 0;
    border-radius: 40px;
    color: var(--docsearch-muted-color);
    cursor: pointer;
    display: flex;
    font-weight: 500;
    height: 36px;
    justify-content: space-between;
    margin: 0 0 0 16px;
    padding: 0 8px;
    user-select: none
}

.DocSearch-Button:active,.DocSearch-Button:focus,.DocSearch-Button:hover {
    background: var(--docsearch-searchbox-focus-background);
    box-shadow: var(--docsearch-searchbox-shadow);
    color: var(--docsearch-text-color);
    outline: none
}

.DocSearch-Button-Container {
    align-items: center;
    display: flex
}

.DocSearch-Search-Icon {
    stroke-width: 1.6
}

.DocSearch-Button .DocSearch-Search-Icon {
    color: var(--docsearch-text-color)
}

.DocSearch-Button-Placeholder {
    font-size: 1rem;
    padding: 0 12px 0 6px
}

.DocSearch-Button-Keys {
    display: flex;
    min-width: calc(40px + .8em)
}

.DocSearch-Button-Key {
    align-items: center;
    background: var(--docsearch-key-gradient);
    border-radius: 3px;
    box-shadow: var(--docsearch-key-shadow);
    color: var(--docsearch-muted-color);
    display: flex;
    height: 18px;
    justify-content: center;
    margin-right: .4em;
    position: relative;
    padding: 0 0 2px;
    border: 0;
    top: -1px;
    width: 20px
}

.DocSearch-Button-Key--pressed {
    transform: translate3d(0,1px,0);
    box-shadow: var(--docsearch-key-pressed-shadow)
}

@media (max-width: 768px) {
    .DocSearch-Button-Keys,.DocSearch-Button-Placeholder {
        display:none
    }
}

.DocSearch--active {
    overflow: hidden!important
}

.DocSearch-Container,.DocSearch-Container * {
    box-sizing: border-box
}

.DocSearch-Container {
    background-color: var(--docsearch-container-background);
    height: 100vh;
    left: 0;
    position: fixed;
    top: 0;
    width: 100vw;
    z-index: 200
}

.DocSearch-Container a {
    text-decoration: none
}

.DocSearch-Link {
    appearance: none;
    background: none;
    border: 0;
    color: var(--docsearch-highlight-color);
    cursor: pointer;
    font: inherit;
    margin: 0;
    padding: 0
}

.DocSearch-Modal {
    background: var(--docsearch-modal-background);
    border-radius: 6px;
    box-shadow: var(--docsearch-modal-shadow);
    flex-direction: column;
    margin: 60px auto auto;
    max-width: var(--docsearch-modal-width);
    position: relative
}

.DocSearch-SearchBar {
    display: flex;
    padding: var(--docsearch-spacing) var(--docsearch-spacing) 0
}

.DocSearch-Form {
    align-items: center;
    background: var(--docsearch-searchbox-focus-background);
    border-radius: 4px;
    box-shadow: var(--docsearch-searchbox-shadow);
    display: flex;
    height: var(--docsearch-searchbox-height);
    margin: 0;
    padding: 0 var(--docsearch-spacing);
    position: relative;
    width: 100%
}

.DocSearch-Input {
    appearance: none;
    background: transparent;
    border: 0;
    color: var(--docsearch-text-color);
    flex: 1;
    font: inherit;
    font-size: 1.2em;
    height: 100%;
    outline: none;
    padding: 0 0 0 8px;
    width: 80%
}

.DocSearch-Input::placeholder {
    color: var(--docsearch-muted-color);
    opacity: 1
}

.DocSearch-Input::-webkit-search-cancel-button,.DocSearch-Input::-webkit-search-decoration,.DocSearch-Input::-webkit-search-results-button,.DocSearch-Input::-webkit-search-results-decoration {
    display: none
}

.DocSearch-LoadingIndicator,.DocSearch-MagnifierLabel,.DocSearch-Reset {
    margin: 0;
    padding: 0
}

.DocSearch-MagnifierLabel,.DocSearch-Reset {
    align-items: center;
    color: var(--docsearch-highlight-color);
    display: flex;
    justify-content: center
}

.DocSearch-Container--Stalled .DocSearch-MagnifierLabel,.DocSearch-LoadingIndicator {
    display: none
}

.DocSearch-Container--Stalled .DocSearch-LoadingIndicator {
    align-items: center;
    color: var(--docsearch-highlight-color);
    display: flex;
    justify-content: center
}

@media screen and (prefers-reduced-motion:reduce) {
    .DocSearch-Reset {
        animation: none;
        appearance: none;
        background: none;
        border: 0;
        border-radius: 50%;
        color: var(--docsearch-icon-color);
        cursor: pointer;
        right: 0;
        stroke-width: var(--docsearch-icon-stroke-width)
    }
}

.DocSearch-Reset {
    animation: fade-in .1s ease-in forwards;
    appearance: none;
    background: none;
    border: 0;
    border-radius: 50%;
    color: var(--docsearch-icon-color);
    cursor: pointer;
    padding: 2px;
    right: 0;
    stroke-width: var(--docsearch-icon-stroke-width)
}

.DocSearch-Reset[hidden] {
    display: none
}

.DocSearch-Reset:hover {
    color: var(--docsearch-highlight-color)
}

.DocSearch-LoadingIndicator svg,.DocSearch-MagnifierLabel svg {
    height: 24px;
    width: 24px
}

.DocSearch-Cancel {
    display: none
}

.DocSearch-Dropdown {
    max-height: calc(var(--docsearch-modal-height) - var(--docsearch-searchbox-height) - var(--docsearch-spacing) - var(--docsearch-footer-height));
    min-height: var(--docsearch-spacing);
    overflow-y: auto;
    overflow-y: overlay;
    padding: 0 var(--docsearch-spacing);
    scrollbar-color: var(--docsearch-muted-color) var(--docsearch-modal-background);
    scrollbar-width: thin
}

.DocSearch-Dropdown::-webkit-scrollbar {
    width: 12px
}

.DocSearch-Dropdown::-webkit-scrollbar-track {
    background: transparent
}

.DocSearch-Dropdown::-webkit-scrollbar-thumb {
    background-color: var(--docsearch-muted-color);
    border: 3px solid var(--docsearch-modal-background);
    border-radius: 20px
}

.DocSearch-Dropdown ul {
    list-style: none;
    margin: 0;
    padding: 0
}

.DocSearch-Label {
    font-size: .75em;
    line-height: 1.6em
}

.DocSearch-Help,.DocSearch-Label {
    color: var(--docsearch-muted-color)
}

.DocSearch-Help {
    font-size: .9em;
    margin: 0;
    user-select: none
}

.DocSearch-Title {
    font-size: 1.2em
}

.DocSearch-Logo a {
    display: flex
}

.DocSearch-Logo svg {
    color: var(--docsearch-logo-color);
    margin-left: 8px
}

.DocSearch-Hits:last-of-type {
    margin-bottom: 24px
}

.DocSearch-Hits mark {
    background: none;
    color: var(--docsearch-highlight-color)
}

.DocSearch-HitsFooter {
    color: var(--docsearch-muted-color);
    display: flex;
    font-size: .85em;
    justify-content: center;
    margin-bottom: var(--docsearch-spacing);
    padding: var(--docsearch-spacing)
}

.DocSearch-HitsFooter a {
    border-bottom: 1px solid;
    color: inherit
}

.DocSearch-Hit {
    border-radius: 4px;
    display: flex;
    padding-bottom: 4px;
    position: relative
}

@media screen and (prefers-reduced-motion:reduce) {
    .DocSearch-Hit--deleting {
        transition: none
    }
}

.DocSearch-Hit--deleting {
    opacity: 0;
    transition: all .25s linear
}

@media screen and (prefers-reduced-motion:reduce) {
    .DocSearch-Hit--favoriting {
        transition: none
    }
}

.DocSearch-Hit--favoriting {
    transform: scale(0);
    transform-origin: top center;
    transition: all .25s linear;
    transition-delay: .25s
}

.DocSearch-Hit a {
    background: var(--docsearch-hit-background);
    border-radius: 4px;
    box-shadow: var(--docsearch-hit-shadow);
    display: block;
    padding-left: var(--docsearch-spacing);
    width: 100%
}

.DocSearch-Hit-source {
    background: var(--docsearch-modal-background);
    color: var(--docsearch-highlight-color);
    font-size: .85em;
    font-weight: 600;
    line-height: 32px;
    margin: 0 -4px;
    padding: 8px 4px 0;
    position: sticky;
    top: 0;
    z-index: 10
}

.DocSearch-Hit-Tree {
    color: var(--docsearch-muted-color);
    height: var(--docsearch-hit-height);
    opacity: .5;
    stroke-width: var(--docsearch-icon-stroke-width);
    width: 24px
}

.DocSearch-Hit[aria-selected=true] a {
    background-color: var(--docsearch-highlight-color)
}

.DocSearch-Hit[aria-selected=true] mark {
    text-decoration: underline
}

.DocSearch-Hit-Container {
    align-items: center;
    color: var(--docsearch-hit-color);
    display: flex;
    flex-direction: row;
    height: var(--docsearch-hit-height);
    padding: 0 var(--docsearch-spacing) 0 0
}

.DocSearch-Hit-icon {
    height: 20px;
    width: 20px
}

.DocSearch-Hit-action,.DocSearch-Hit-icon {
    color: var(--docsearch-muted-color);
    stroke-width: var(--docsearch-icon-stroke-width)
}

.DocSearch-Hit-action {
    align-items: center;
    display: flex;
    height: 22px;
    width: 22px
}

.DocSearch-Hit-action svg {
    display: block;
    height: 18px;
    width: 18px
}

.DocSearch-Hit-action+.DocSearch-Hit-action {
    margin-left: 6px
}

.DocSearch-Hit-action-button {
    appearance: none;
    background: none;
    border: 0;
    border-radius: 50%;
    color: inherit;
    cursor: pointer;
    padding: 2px
}

svg.DocSearch-Hit-Select-Icon {
    display: none
}

.DocSearch-Hit[aria-selected=true] .DocSearch-Hit-Select-Icon {
    display: block
}

.DocSearch-Hit-action-button:focus,.DocSearch-Hit-action-button:hover {
    background: rgba(0,0,0,.2);
    transition: background-color .1s ease-in
}

@media screen and (prefers-reduced-motion:reduce) {
    .DocSearch-Hit-action-button:focus,.DocSearch-Hit-action-button:hover {
        transition: none
    }
}

.DocSearch-Hit-action-button:focus path,.DocSearch-Hit-action-button:hover path {
    fill: #fff
}

.DocSearch-Hit-content-wrapper {
    display: flex;
    flex: 1 1 auto;
    flex-direction: column;
    font-weight: 500;
    justify-content: center;
    line-height: 1.2em;
    margin: 0 8px;
    overflow-x: hidden;
    position: relative;
    text-overflow: ellipsis;
    white-space: nowrap;
    width: 80%
}

.DocSearch-Hit-title {
    font-size: .9em
}

.DocSearch-Hit-path {
    color: var(--docsearch-muted-color);
    font-size: .75em
}

.DocSearch-Hit[aria-selected=true] .DocSearch-Hit-action,.DocSearch-Hit[aria-selected=true] .DocSearch-Hit-icon,.DocSearch-Hit[aria-selected=true] .DocSearch-Hit-path,.DocSearch-Hit[aria-selected=true] .DocSearch-Hit-text,.DocSearch-Hit[aria-selected=true] .DocSearch-Hit-title,.DocSearch-Hit[aria-selected=true] .DocSearch-Hit-Tree,.DocSearch-Hit[aria-selected=true] mark {
    color: var(--docsearch-hit-active-color)!important
}

@media screen and (prefers-reduced-motion:reduce) {
    .DocSearch-Hit-action-button:focus,.DocSearch-Hit-action-button:hover {
        background: rgba(0,0,0,.2);
        transition: none
    }
}

.DocSearch-ErrorScreen,.DocSearch-NoResults,.DocSearch-StartScreen {
    font-size: .9em;
    margin: 0 auto;
    padding: 36px 0;
    text-align: center;
    width: 80%
}

.DocSearch-Screen-Icon {
    color: var(--docsearch-muted-color);
    padding-bottom: 12px
}

.DocSearch-NoResults-Prefill-List {
    display: inline-block;
    padding-bottom: 24px;
    text-align: left
}

.DocSearch-NoResults-Prefill-List ul {
    display: inline-block;
    padding: 8px 0 0
}

.DocSearch-NoResults-Prefill-List li {
    list-style-position: inside;
    list-style-type: "» "
}

.DocSearch-Prefill {
    appearance: none;
    background: none;
    border: 0;
    border-radius: 1em;
    color: var(--docsearch-highlight-color);
    cursor: pointer;
    display: inline-block;
    font-size: 1em;
    font-weight: 700;
    padding: 0
}

.DocSearch-Prefill:focus,.DocSearch-Prefill:hover {
    outline: none;
    text-decoration: underline
}

.DocSearch-Footer {
    align-items: center;
    background: var(--docsearch-footer-background);
    border-radius: 0 0 8px 8px;
    box-shadow: var(--docsearch-footer-shadow);
    display: flex;
    flex-direction: row-reverse;
    flex-shrink: 0;
    height: var(--docsearch-footer-height);
    justify-content: space-between;
    padding: 0 var(--docsearch-spacing);
    position: relative;
    user-select: none;
    width: 100%;
    z-index: 300
}

.DocSearch-Commands {
    color: var(--docsearch-muted-color);
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0
}

.DocSearch-Commands li {
    align-items: center;
    display: flex
}

.DocSearch-Commands li:not(:last-of-type) {
    margin-right: .8em
}

.DocSearch-Commands-Key {
    align-items: center;
    background: var(--docsearch-key-gradient);
    border-radius: 2px;
    box-shadow: var(--docsearch-key-shadow);
    display: flex;
    height: 18px;
    justify-content: center;
    margin-right: .4em;
    padding: 0 0 1px;
    color: var(--docsearch-muted-color);
    border: 0;
    width: 20px
}

.DocSearch-VisuallyHiddenForAccessibility {
    clip: rect(0 0 0 0);
    clip-path: inset(50%);
    height: 1px;
    overflow: hidden;
    position: absolute;
    white-space: nowrap;
    width: 1px
}

@media (max-width: 768px) {
    :root {
        --docsearch-spacing:10px;
        --docsearch-footer-height: 40px
    }

    .DocSearch-Dropdown {
        height: 100%
    }

    .DocSearch-Container {
        height: 100vh;
        height: -webkit-fill-available;
        height: calc(var(--docsearch-vh, 1vh)*100);
        position: absolute
    }

    .DocSearch-Footer {
        border-radius: 0;
        bottom: 0;
        position: absolute
    }

    .DocSearch-Hit-content-wrapper {
        display: flex;
        position: relative;
        width: 80%
    }

    .DocSearch-Modal {
        border-radius: 0;
        box-shadow: none;
        height: 100vh;
        height: -webkit-fill-available;
        height: calc(var(--docsearch-vh, 1vh)*100);
        margin: 0;
        max-width: 100%;
        width: 100%
    }

    .DocSearch-Dropdown {
        max-height: calc(var(--docsearch-vh, 1vh)*100 - var(--docsearch-searchbox-height) - var(--docsearch-spacing) - var(--docsearch-footer-height))
    }

    .DocSearch-Cancel {
        appearance: none;
        background: none;
        border: 0;
        color: var(--docsearch-highlight-color);
        cursor: pointer;
        display: inline-block;
        flex: none;
        font: inherit;
        font-size: 1em;
        font-weight: 500;
        margin-left: var(--docsearch-spacing);
        outline: none;
        overflow: hidden;
        padding: 0;
        user-select: none;
        white-space: nowrap
    }

    .DocSearch-Commands,.DocSearch-Hit-Tree {
        display: none
    }
}

@keyframes fade-in {
    0% {
        opacity: 0
    }

    to {
        opacity: 1
    }
}

</style>
<style>
    /*!
 * Bootstrap Docs (https://getbootstrap.com/)
 * Copyright 2011-2024 The Bootstrap Authors
 * Licensed under the Creative Commons Attribution 3.0 Unported License.
 * For details, see https://creativecommons.org/licenses/by/3.0/.
 */
 :root {
    --bs-breakpoint-xs: 0;
    --bs-breakpoint-sm: 576px;
    --bs-breakpoint-md: 768px;
    --bs-breakpoint-lg: 992px;
    --bs-breakpoint-xl: 1200px;
    --bs-breakpoint-xxl: 1400px
}

.grid {
    display: grid;
    grid-template-rows: repeat(var(--bs-rows, 1), 1fr);
    grid-template-columns: repeat(var(--bs-columns, 12), 1fr);
    gap: var(--bs-gap, 1.5rem)
}

.grid .g-col-1 {
    grid-column: auto/span 1
}

.grid .g-col-2 {
    grid-column: auto/span 2
}

.grid .g-col-3 {
    grid-column: auto/span 3
}

.grid .g-col-4 {
    grid-column: auto/span 4
}

.grid .g-col-5 {
    grid-column: auto/span 5
}

.grid .g-col-6 {
    grid-column: auto/span 6
}

.grid .g-col-7 {
    grid-column: auto/span 7
}

.grid .g-col-8 {
    grid-column: auto/span 8
}

.grid .g-col-9 {
    grid-column: auto/span 9
}

.grid .g-col-10 {
    grid-column: auto/span 10
}

.grid .g-col-11 {
    grid-column: auto/span 11
}

.grid .g-col-12 {
    grid-column: auto/span 12
}

.grid .g-start-1 {
    grid-column-start: 1
}

.grid .g-start-2 {
    grid-column-start: 2
}

.grid .g-start-3 {
    grid-column-start: 3
}

.grid .g-start-4 {
    grid-column-start: 4
}

.grid .g-start-5 {
    grid-column-start: 5
}

.grid .g-start-6 {
    grid-column-start: 6
}

.grid .g-start-7 {
    grid-column-start: 7
}

.grid .g-start-8 {
    grid-column-start: 8
}

.grid .g-start-9 {
    grid-column-start: 9
}

.grid .g-start-10 {
    grid-column-start: 10
}

.grid .g-start-11 {
    grid-column-start: 11
}

@media (min-width: 576px) {
    .grid .g-col-sm-1 {
        grid-column:auto/span 1
    }

    .grid .g-col-sm-2 {
        grid-column: auto/span 2
    }

    .grid .g-col-sm-3 {
        grid-column: auto/span 3
    }

    .grid .g-col-sm-4 {
        grid-column: auto/span 4
    }

    .grid .g-col-sm-5 {
        grid-column: auto/span 5
    }

    .grid .g-col-sm-6 {
        grid-column: auto/span 6
    }

    .grid .g-col-sm-7 {
        grid-column: auto/span 7
    }

    .grid .g-col-sm-8 {
        grid-column: auto/span 8
    }

    .grid .g-col-sm-9 {
        grid-column: auto/span 9
    }

    .grid .g-col-sm-10 {
        grid-column: auto/span 10
    }

    .grid .g-col-sm-11 {
        grid-column: auto/span 11
    }

    .grid .g-col-sm-12 {
        grid-column: auto/span 12
    }

    .grid .g-start-sm-1 {
        grid-column-start: 1
    }

    .grid .g-start-sm-2 {
        grid-column-start: 2
    }

    .grid .g-start-sm-3 {
        grid-column-start: 3
    }

    .grid .g-start-sm-4 {
        grid-column-start: 4
    }

    .grid .g-start-sm-5 {
        grid-column-start: 5
    }

    .grid .g-start-sm-6 {
        grid-column-start: 6
    }

    .grid .g-start-sm-7 {
        grid-column-start: 7
    }

    .grid .g-start-sm-8 {
        grid-column-start: 8
    }

    .grid .g-start-sm-9 {
        grid-column-start: 9
    }

    .grid .g-start-sm-10 {
        grid-column-start: 10
    }

    .grid .g-start-sm-11 {
        grid-column-start: 11
    }
}

@media (min-width: 768px) {
    .grid .g-col-md-1 {
        grid-column:auto/span 1
    }

    .grid .g-col-md-2 {
        grid-column: auto/span 2
    }

    .grid .g-col-md-3 {
        grid-column: auto/span 3
    }

    .grid .g-col-md-4 {
        grid-column: auto/span 4
    }

    .grid .g-col-md-5 {
        grid-column: auto/span 5
    }

    .grid .g-col-md-6 {
        grid-column: auto/span 6
    }

    .grid .g-col-md-7 {
        grid-column: auto/span 7
    }

    .grid .g-col-md-8 {
        grid-column: auto/span 8
    }

    .grid .g-col-md-9 {
        grid-column: auto/span 9
    }

    .grid .g-col-md-10 {
        grid-column: auto/span 10
    }

    .grid .g-col-md-11 {
        grid-column: auto/span 11
    }

    .grid .g-col-md-12 {
        grid-column: auto/span 12
    }

    .grid .g-start-md-1 {
        grid-column-start: 1
    }

    .grid .g-start-md-2 {
        grid-column-start: 2
    }

    .grid .g-start-md-3 {
        grid-column-start: 3
    }

    .grid .g-start-md-4 {
        grid-column-start: 4
    }

    .grid .g-start-md-5 {
        grid-column-start: 5
    }

    .grid .g-start-md-6 {
        grid-column-start: 6
    }

    .grid .g-start-md-7 {
        grid-column-start: 7
    }

    .grid .g-start-md-8 {
        grid-column-start: 8
    }

    .grid .g-start-md-9 {
        grid-column-start: 9
    }

    .grid .g-start-md-10 {
        grid-column-start: 10
    }

    .grid .g-start-md-11 {
        grid-column-start: 11
    }
}

@media (min-width: 992px) {
    .grid .g-col-lg-1 {
        grid-column:auto/span 1
    }

    .grid .g-col-lg-2 {
        grid-column: auto/span 2
    }

    .grid .g-col-lg-3 {
        grid-column: auto/span 3
    }

    .grid .g-col-lg-4 {
        grid-column: auto/span 4
    }

    .grid .g-col-lg-5 {
        grid-column: auto/span 5
    }

    .grid .g-col-lg-6 {
        grid-column: auto/span 6
    }

    .grid .g-col-lg-7 {
        grid-column: auto/span 7
    }

    .grid .g-col-lg-8 {
        grid-column: auto/span 8
    }

    .grid .g-col-lg-9 {
        grid-column: auto/span 9
    }

    .grid .g-col-lg-10 {
        grid-column: auto/span 10
    }

    .grid .g-col-lg-11 {
        grid-column: auto/span 11
    }

    .grid .g-col-lg-12 {
        grid-column: auto/span 12
    }

    .grid .g-start-lg-1 {
        grid-column-start: 1
    }

    .grid .g-start-lg-2 {
        grid-column-start: 2
    }

    .grid .g-start-lg-3 {
        grid-column-start: 3
    }

    .grid .g-start-lg-4 {
        grid-column-start: 4
    }

    .grid .g-start-lg-5 {
        grid-column-start: 5
    }

    .grid .g-start-lg-6 {
        grid-column-start: 6
    }

    .grid .g-start-lg-7 {
        grid-column-start: 7
    }

    .grid .g-start-lg-8 {
        grid-column-start: 8
    }

    .grid .g-start-lg-9 {
        grid-column-start: 9
    }

    .grid .g-start-lg-10 {
        grid-column-start: 10
    }

    .grid .g-start-lg-11 {
        grid-column-start: 11
    }
}

@media (min-width: 1200px) {
    .grid .g-col-xl-1 {
        grid-column:auto/span 1
    }

    .grid .g-col-xl-2 {
        grid-column: auto/span 2
    }

    .grid .g-col-xl-3 {
        grid-column: auto/span 3
    }

    .grid .g-col-xl-4 {
        grid-column: auto/span 4
    }

    .grid .g-col-xl-5 {
        grid-column: auto/span 5
    }

    .grid .g-col-xl-6 {
        grid-column: auto/span 6
    }

    .grid .g-col-xl-7 {
        grid-column: auto/span 7
    }

    .grid .g-col-xl-8 {
        grid-column: auto/span 8
    }

    .grid .g-col-xl-9 {
        grid-column: auto/span 9
    }

    .grid .g-col-xl-10 {
        grid-column: auto/span 10
    }

    .grid .g-col-xl-11 {
        grid-column: auto/span 11
    }

    .grid .g-col-xl-12 {
        grid-column: auto/span 12
    }

    .grid .g-start-xl-1 {
        grid-column-start: 1
    }

    .grid .g-start-xl-2 {
        grid-column-start: 2
    }

    .grid .g-start-xl-3 {
        grid-column-start: 3
    }

    .grid .g-start-xl-4 {
        grid-column-start: 4
    }

    .grid .g-start-xl-5 {
        grid-column-start: 5
    }

    .grid .g-start-xl-6 {
        grid-column-start: 6
    }

    .grid .g-start-xl-7 {
        grid-column-start: 7
    }

    .grid .g-start-xl-8 {
        grid-column-start: 8
    }

    .grid .g-start-xl-9 {
        grid-column-start: 9
    }

    .grid .g-start-xl-10 {
        grid-column-start: 10
    }

    .grid .g-start-xl-11 {
        grid-column-start: 11
    }
}

@media (min-width: 1400px) {
    .grid .g-col-xxl-1 {
        grid-column:auto/span 1
    }

    .grid .g-col-xxl-2 {
        grid-column: auto/span 2
    }

    .grid .g-col-xxl-3 {
        grid-column: auto/span 3
    }

    .grid .g-col-xxl-4 {
        grid-column: auto/span 4
    }

    .grid .g-col-xxl-5 {
        grid-column: auto/span 5
    }

    .grid .g-col-xxl-6 {
        grid-column: auto/span 6
    }

    .grid .g-col-xxl-7 {
        grid-column: auto/span 7
    }

    .grid .g-col-xxl-8 {
        grid-column: auto/span 8
    }

    .grid .g-col-xxl-9 {
        grid-column: auto/span 9
    }

    .grid .g-col-xxl-10 {
        grid-column: auto/span 10
    }

    .grid .g-col-xxl-11 {
        grid-column: auto/span 11
    }

    .grid .g-col-xxl-12 {
        grid-column: auto/span 12
    }

    .grid .g-start-xxl-1 {
        grid-column-start: 1
    }

    .grid .g-start-xxl-2 {
        grid-column-start: 2
    }

    .grid .g-start-xxl-3 {
        grid-column-start: 3
    }

    .grid .g-start-xxl-4 {
        grid-column-start: 4
    }

    .grid .g-start-xxl-5 {
        grid-column-start: 5
    }

    .grid .g-start-xxl-6 {
        grid-column-start: 6
    }

    .grid .g-start-xxl-7 {
        grid-column-start: 7
    }

    .grid .g-start-xxl-8 {
        grid-column-start: 8
    }

    .grid .g-start-xxl-9 {
        grid-column-start: 9
    }

    .grid .g-start-xxl-10 {
        grid-column-start: 10
    }

    .grid .g-start-xxl-11 {
        grid-column-start: 11
    }
}

:root,[data-bs-theme="light"] {
    --bd-purple: #4c0bce;
    --bd-violet: #712cf9;
    --bd-accent: #ffe484;
    --bd-violet-rgb: 112.520718,44.062154,249.437846;
    --bd-accent-rgb: 255,228,132;
    --bd-pink-rgb: 214,51,132;
    --bd-teal-rgb: 32,201,151;
    --bd-violet-bg: var(--bd-violet);
    --bd-toc-color: var(--bd-violet);
    --bd-sidebar-link-bg: rgba(var(--bd-violet-rgb), .1);
    --bd-callout-link: 10,88,202;
    --bd-callout-code-color: #ab296a;
    --bd-pre-bg: var(--bs-tertiary-bg)
}

[data-bs-theme="dark"] {
    --bd-violet: #9461fb;
    --bd-violet-bg: #712cf9;
    --bd-toc-color: var(--bs-emphasis-color);
    --bd-sidebar-link-bg: rgba(84,33,187, .5);
    --bd-callout-link: 110,168,254;
    --bd-callout-code-color: #e685b5;
    --bd-pre-bg: #1b1f22
}

.bd-navbar {
    padding: .75rem 0;
    background-color: transparent;
    box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.15),inset 0 -1px 0 rgba(255,255,255,0.15)
}

.bd-navbar::after {
    position: absolute;
    inset: 0;
    z-index: -1;
    display: block;
    content: "";
    background-image: linear-gradient(rgba(var(--bd-violet-rgb), 1), rgba(var(--bd-violet-rgb), 0.95))
}

@media (max-width: 991.98px) {
    .bd-navbar .bd-navbar-toggle {
        width:4.25rem
    }
}

.bd-navbar .navbar-toggler {
    padding: 0;
    margin-right: -.5rem;
    border: 0
}

.bd-navbar .navbar-toggler:first-child {
    margin-left: -.5rem
}

.bd-navbar .navbar-toggler .bi {
    width: 1.5rem;
    height: 1.5rem
}

.bd-navbar .navbar-toggler:focus {
    box-shadow: none
}

.bd-navbar .navbar-brand {
    color: #fff;
    transition: transform 0.2s ease-in-out
}

@media (prefers-reduced-motion: reduce) {
    .bd-navbar .navbar-brand {
        transition: none
    }
}

.bd-navbar .navbar-brand:hover {
    transform: rotate(-5deg) scale(1.1)
}

.bd-navbar .navbar-toggler,.bd-navbar .nav-link {
    padding-right: .25rem;
    padding-left: .25rem;
    color: rgba(255,255,255,0.85)
}

.bd-navbar .navbar-toggler:hover,.bd-navbar .navbar-toggler:focus,.bd-navbar .nav-link:hover,.bd-navbar .nav-link:focus {
    color: #fff
}

.bd-navbar .navbar-toggler.active,.bd-navbar .nav-link.active {
    font-weight: 600;
    color: #fff
}

.bd-navbar .navbar-nav-svg {
    display: inline-block;
    vertical-align: -.125rem
}

.bd-navbar .offcanvas-lg {
    background-color: var(--bd-violet-bg);
    border-left: 0
}

@media (max-width: 991.98px) {
    .bd-navbar .offcanvas-lg {
        box-shadow:var(--bs-box-shadow-lg)
    }
}

.bd-navbar .dropdown-toggle:focus:not(:focus-visible) {
    outline: 0
}

.bd-navbar .dropdown-menu {
    --bs-dropdown-min-width: 12rem;
    --bs-dropdown-padding-x: .25rem;
    --bs-dropdown-padding-y: .25rem;
    --bs-dropdown-link-hover-bg: rgba(var(--bd-violet-rgb), .1);
    --bs-dropdown-link-active-bg: rgba(var(--bd-violet-rgb), 1);
    --bs-dropdown-font-size: .875rem;
    font-size: .875rem;
    border-radius: .5rem;
    box-shadow: var(--bs-box-shadow)
}

.bd-navbar .dropdown-menu li+li {
    margin-top: .125rem
}

.bd-navbar .dropdown-menu .dropdown-item {
    border-radius: .25rem
}

.bd-navbar .dropdown-menu .dropdown-item:active .bi {
    color: inherit !important
}

.bd-navbar .dropdown-menu .active {
    font-weight: 600
}

.bd-navbar .dropdown-menu .active .bi {
    display: block !important
}

.bd-navbar .dropdown-menu-end {
    --bs-dropdown-min-width: 8rem
}

[data-bs-theme="dark"] .bd-navbar {
    box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.15),inset 0 -1px 0 rgba(255,255,255,0.15)
}

:root {
    --docsearch-primary-color: var(--bd-violet);
    --docsearch-logo-color: var(--bd-violet)
}

[data-bs-theme="dark"] {
    --docsearch-text-color: #f5f6f7;
    --docsearch-container-background: rgba(9, 10, 17, .8);
    --docsearch-modal-background: #15172a;
    --docsearch-modal-shadow: inset 1px 1px 0 0 #2c2e40, 0 3px 8px 0 #000309;
    --docsearch-searchbox-background: #090a11;
    --docsearch-searchbox-focus-background: #000;
    --docsearch-hit-color: #bec3c9;
    --docsearch-hit-shadow: none;
    --docsearch-hit-background: #090a11;
    --docsearch-key-gradient: linear-gradient(-26.5deg, #565872, #31355b);
    --docsearch-key-shadow: inset 0 -2px 0 0 #282d55, inset 0 0 1px 1px #51577d, 0 2px 2px 0 rgba(3, 4, 9, .3);
    --docsearch-footer-background: #1e2136;
    --docsearch-footer-shadow: inset 0 1px 0 0 rgba(73, 76, 106, .5), 0 -4px 8px 0 rgba(0, 0, 0, .2);
    --docsearch-muted-color: #7f8497
}

.bd-search {
    position: relative
}

@media (min-width: 992px) {
    .bd-search {
        position:absolute;
        top: .875rem;
        left: 50%;
        width: 200px;
        margin-left: -100px
    }
}

@media (min-width: 1200px) {
    .bd-search {
        width:280px;
        margin-left: -140px
    }
}

.DocSearch-Container {
    --docsearch-muted-color: var(--bs-secondary-color);
    --docsearch-hit-shadow: none;
    z-index: 2000;
    cursor: auto
}

@media (min-width: 992px) {
    .DocSearch-Container {
        padding-top:4rem
    }
}

.DocSearch-Button {
    --docsearch-searchbox-background: rgba(0,0,0,0.1);
    --docsearch-searchbox-color: #fff;
    --docsearch-searchbox-focus-background: rgba(0,0,0,0.25);
    --docsearch-searchbox-shadow: 0 0 0 0.25rem rgba(255,228,132,0.4);
    --docsearch-text-color: #fff;
    --docsearch-muted-color: rgba(255,255,255,0.65);
    width: 100%;
    height: 38px;
    margin: 0;
    border: 1px solid rgba(255,255,255,0.4);
    border-radius: .375rem
}

.DocSearch-Button .DocSearch-Search-Icon {
    opacity: .65
}

.DocSearch-Button:active,.DocSearch-Button:focus,.DocSearch-Button:hover {
    border-color: #ffe484
}

.DocSearch-Button:active .DocSearch-Search-Icon,.DocSearch-Button:focus .DocSearch-Search-Icon,.DocSearch-Button:hover .DocSearch-Search-Icon {
    opacity: 1
}

@media (max-width: 991.98px) {
    .DocSearch-Button,.DocSearch-Button:hover,.DocSearch-Button:focus {
        background:transparent;
        border: 0;
        box-shadow: none
    }

    .DocSearch-Button:focus {
        box-shadow: var(--docsearch-searchbox-shadow)
    }
}

@media (max-width: 991.98px) {
    .DocSearch-Button-Keys,.DocSearch-Button-Placeholder {
        display:none
    }
}

.DocSearch-Button-Keys {
    min-width: 0;
    padding: .125rem .25rem;
    background: rgba(0,0,0,0.25);
    border-radius: .25rem
}

.DocSearch-Button-Key {
    top: 0;
    width: auto;
    height: 1.25rem;
    padding-right: .125rem;
    padding-left: .125rem;
    margin-right: 0;
    font-size: .875rem;
    background: none;
    box-shadow: none
}

.DocSearch-Commands-Key {
    padding-left: 1px;
    font-size: .875rem;
    background-color: rgba(0,0,0,0.1);
    background-image: none;
    box-shadow: none
}

.DocSearch-Form {
    border-radius: var(--bs-border-radius)
}

.DocSearch-Hits mark {
    padding: 0
}

.DocSearch-Hit {
    padding-bottom: 0;
    border-radius: 0
}

.DocSearch-Hit a {
    border-radius: 0;
    border: solid var(--bs-border-color);
    border-width: 0 1px 1px
}

.DocSearch-Hit:first-child a {
    border-top-left-radius: var(--bs-border-radius);
    border-top-right-radius: var(--bs-border-radius);
    border-top-width: 1px
}

.DocSearch-Hit:last-child a {
    border-bottom-right-radius: var(--bs-border-radius);
    border-bottom-left-radius: var(--bs-border-radius)
}

.DocSearch-Hit-icon {
    display: flex;
    align-items: center
}

.DocSearch-Logo svg .cls-1,.DocSearch-Logo svg .cls-2 {
    fill: var(--docsearch-logo-color)
}

.bd-masthead {
    --bd-pink-rgb: 214,51,132;
    padding: 3rem 0;
    background-image: linear-gradient(180deg, rgba(var(--bs-body-bg-rgb), 0.01), rgba(var(--bs-body-bg-rgb), 1) 85%),radial-gradient(ellipse at top left, rgba(var(--bs-primary-rgb), 0.5), transparent 50%),radial-gradient(ellipse at top right, rgba(var(--bd-accent-rgb), 0.5), transparent 50%),radial-gradient(ellipse at center right, rgba(var(--bd-violet-rgb), 0.5), transparent 50%),radial-gradient(ellipse at center left, rgba(var(--bd-pink-rgb), 0.5), transparent 50%)
}

.bd-masthead h1 {
    --bs-heading-color: var(--bs-emphasis-color);
    font-size: calc(1.525rem + 3.3vw)
}

@media (min-width: 1200px) {
    .bd-masthead h1 {
        font-size:4rem
    }
}

.bd-masthead .lead {
    font-size: 1rem;
    font-weight: 400;
    color: var(--bs-secondary-color)
}

.bd-masthead .bd-code-snippet {
    margin: 0;
    border-color: var(--bs-border-color-translucent);
    border-width: 1px;
    border-radius: .5rem
}

.bd-masthead .highlight {
    width: 100%;
    padding: .5rem 1rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    background-color: rgba(var(--bs-body-color-rgb), 0.075);
    border-radius: calc(.5rem - 1px)
}

@media (min-width: 992px) {
    .bd-masthead .highlight {
        padding-right:4rem
    }
}

.bd-masthead .highlight pre {
    padding: 0;
    margin: .625rem 0;
    overflow: hidden
}

.bd-masthead .btn-clipboard {
    position: absolute;
    top: -.625rem;
    right: 0;
    background-color: transparent
}

.bd-masthead #carbonads {
    margin-inline:auto}

@media (min-width: 768px) {
    .bd-masthead .lead {
        font-size:calc(1.275rem + .3vw)
    }
}

@media (min-width: 768px) and (min-width: 1200px) {
    .bd-masthead .lead {
        font-size:1.5rem
    }
}

.masthead-followup h2,.masthead-followup h3,.masthead-followup h4 {
    --bs-heading-color: var(--bs-emphasis-color)
}

.masthead-followup .lead {
    font-size: 1rem
}

@media (min-width: 768px) {
    .masthead-followup .lead {
        font-size:1.25rem
    }
}

.masthead-followup-icon {
    padding: 1rem;
    color: rgba(var(--bg-rgb), 1);
    background-color: rgba(var(--bg-rgb), 0.1);
    background-blend-mode: multiple;
    border-radius: 1rem;
    mix-blend-mode: darken
}

.masthead-followup-icon svg {
    filter: drop-shadow(0 1px 1px var(--bs-body-bg))
}

.masthead-notice {
    background-color: var(--bd-accent);
    box-shadow: inset 0 -1px 1px rgba(var(--bs-body-color-rgb), 0.15),0 0.25rem 1.5rem rgba(var(--bs-body-bg-rgb), 0.75)
}

.animate-img>img {
    transition: transform 0.2s ease-in-out
}

@media (prefers-reduced-motion: reduce) {
    .animate-img>img {
        transition: none
    }
}

.animate-img:hover>img {
    transform: scale(1.1)
}

[data-bs-theme="dark"] .masthead-followup-icon {
    mix-blend-mode: lighten
}

#carbonads {
    position: static;
    display: block;
    max-width: 400px;
    padding: 15px 15px 15px 160px;
    margin: 2rem 0;
    overflow: hidden;
    font-size: .8125rem;
    line-height: 1.4;
    text-align: left;
    background-color: var(--bs-tertiary-bg)
}

#carbonads a {
    color: var(--bs-body-color);
    text-decoration: none
}

@media (min-width: 576px) {
    #carbonads {
        border-radius:.5rem
    }
}

.carbon-img {
    float: left;
    margin-left: -145px
}

.carbon-poweredby {
    display: block;
    margin-top: .75rem;
    color: var(--bs-body-color) !important
}

.bd-content>h2,.bd-content>h3,.bd-content>h4 {
    --bs-heading-color: var(--bs-emphasis-color)
}

.bd-content>h2:not(:first-child) {
    margin-top: 3rem
}

.bd-content>h3 {
    margin-top: 2rem
}

.bd-content>ul li,.bd-content>ol li {
    margin-bottom: .25rem
}

.bd-content>ul li>p~ul,.bd-content>ol li>p~ul {
    margin-top: -.5rem;
    margin-bottom: 1rem
}

.bd-content>.table,.bd-content>.table-responsive .table {
    --bs-table-border-color: var(--bs-border-color);
    max-width: 100%;
    margin-bottom: 1.5rem;
    font-size: .875rem
}

@media (max-width: 991.98px) {
    .bd-content>.table.table-bordered,.bd-content>.table-responsive .table.table-bordered {
        border:0
    }
}

.bd-content>.table thead,.bd-content>.table-responsive .table thead {
    border-bottom: 2px solid currentcolor
}

.bd-content>.table tbody:not(:first-child),.bd-content>.table-responsive .table tbody:not(:first-child) {
    border-top: 2px solid currentcolor
}

.bd-content>.table th:first-child,.bd-content>.table td:first-child,.bd-content>.table-responsive .table th:first-child,.bd-content>.table-responsive .table td:first-child {
    padding-left: 0
}

.bd-content>.table th:not(:last-child),.bd-content>.table td:not(:last-child),.bd-content>.table-responsive .table th:not(:last-child),.bd-content>.table-responsive .table td:not(:last-child) {
    padding-right: 1.5rem
}

.bd-content>.table th,.bd-content>.table-responsive .table th {
    color: var(--bs-emphasis-color)
}

.bd-content>.table strong,.bd-content>.table-responsive .table strong {
    color: var(--bs-emphasis-color)
}

.bd-content>.table th,.bd-content>.table td:first-child>code,.bd-content>.table-responsive .table th,.bd-content>.table-responsive .table td:first-child>code {
    white-space: nowrap
}

.table-options td:nth-child(2) {
    min-width: 160px
}

.table-options td:last-child,.table-utilities td:last-child {
    min-width: 280px
}

.table-swatches th {
    color: var(--bs-emphasis-color)
}

.table-swatches td code {
    white-space: nowrap
}

.bd-title {
    --bs-heading-color: var(--bs-emphasis-color);
    font-size: calc(1.425rem + 2.1vw)
}

@media (min-width: 1200px) {
    .bd-title {
        font-size:3rem
    }
}

.bd-lead {
    font-size: calc(1.275rem + .3vw);
    font-weight: 300
}

@media (min-width: 1200px) {
    .bd-lead {
        font-size:1.5rem
    }
}

.bi {
    width: 1em;
    height: 1em;
    vertical-align: -.125em;
    fill: currentcolor
}

@media (min-width: 992px) {
    .border-lg-start {
        border-left:var(--bs-border-width) solid var(--bs-border-color)
    }
}

.bd-summary-link {
    color: var(--bs-link-color)
}

.bd-summary-link:hover,details[open]>.bd-summary-link {
    color: var(--bs-link-hover-color)
}

[data-bs-theme="blue"] {
    --bs-body-color: var(--bs-white);
    --bs-body-color-rgb: 255,255,255;
    --bs-body-bg: var(--bs-blue);
    --bs-body-bg-rgb: 13,110,253;
    --bs-tertiary-bg: #0a58ca
}

[data-bs-theme="blue"] .dropdown-menu {
    --bs-dropdown-bg: #0c63e4;
    --bs-dropdown-link-active-bg: #084298
}

[data-bs-theme="blue"] .btn-secondary {
    --bs-btn-bg: #3d8bfc;
    --bs-btn-border-color: rgba(255,255,255,0.25);
    --bs-btn-hover-bg: #247cfc;
    --bs-btn-hover-border-color: rgba(255,255,255,0.25);
    --bs-btn-active-bg: #0b6dfb;
    --bs-btn-active-border-color: rgba(255,255,255,0.5);
    --bs-btn-focus-border-color: rgba(255,255,255,0.5);
    --bs-btn-focus-box-shadow: 0 0 0 .25rem rgba(255, 255, 255, .2)
}

.skippy {
    background-color: #4c0bce
}

.skippy a {
    color: #fff
}

@media (min-width: 992px) {
    .bd-sidebar {
        position:-webkit-sticky;
        position: sticky;
        top: 5rem;
        display: block !important;
        height: calc(100vh - 6rem);
        padding-left: .25rem;
        margin-left: -.25rem;
        overflow-y: auto
    }
}

@media (max-width: 991.98px) {
    .bd-sidebar .offcanvas-lg {
        border-right-color:var(--bs-border-color);
        box-shadow: var(--bs-box-shadow-lg)
    }
}

.bd-links-heading {
    color: var(--bs-emphasis-color)
}

@media (max-width: 991.98px) {
    .bd-links-nav {
        font-size:.875rem
    }
}

@media (max-width: 991.98px) {
    .bd-links-nav {
        -moz-column-count:2;
        column-count: 2;
        -moz-column-gap: 1.5rem;
        column-gap: 1.5rem
    }

    .bd-links-nav .bd-links-group {
        -moz-column-break-inside: avoid;
        break-inside: avoid
    }

    .bd-links-nav .bd-links-span-all {
        -moz-column-span: all;
        column-span: all
    }
}

.bd-links-link {
    padding: .1875rem .5rem;
    margin-top: .125rem;
    margin-left: 1.125rem;
    color: var(--bs-body-color);
    text-decoration: none
}

.bd-links-link:hover,.bd-links-link:focus,.bd-links-link.active {
    color: var(--bs-emphasis-color);
    background-color: var(--bd-sidebar-link-bg)
}

.bd-links-link.active {
    font-weight: 600
}

.bd-gutter {
    --bs-gutter-x: 3rem
}

@media (min-width: 992px) {
    .bd-layout {
        display:grid;
        grid-template-areas: "sidebar main";
        grid-template-columns: 1fr 5fr;
        gap: 1.5rem
    }
}

.bd-sidebar {
    grid-area: sidebar
}

.bd-main {
    grid-area: main
}

@media (max-width: 991.98px) {
    .bd-main {
        max-width:760px;
        margin-inline:auto}
}

@media (min-width: 768px) {
    .bd-main {
        display:grid;
        grid-template-areas: "intro" "toc" "content";
        grid-template-rows: auto auto 1fr;
        gap: inherit
    }
}

@media (min-width: 992px) {
    .bd-main {
        grid-template-areas:"intro   toc" "content toc";
        grid-template-rows: auto 1fr;
        grid-template-columns: 4fr 1fr
    }
}

.bd-intro {
    grid-area: intro
}

.bd-toc {
    grid-area: toc
}

.bd-content {
    grid-area: content;
    min-width: 1px
}

@media (min-width: 992px) {
    .bd-toc {
        position:-webkit-sticky;
        position: sticky;
        top: 5rem;
        right: 0;
        z-index: 2;
        height: calc(100vh - 7rem);
        overflow-y: auto
    }
}

.bd-toc nav {
    font-size: .875rem
}

.bd-toc nav ul {
    padding-left: 0;
    margin-bottom: 0;
    list-style: none
}

.bd-toc nav ul ul {
    padding-left: 1rem
}

.bd-toc nav a {
    display: block;
    padding: .125rem 0 .125rem .75rem;
    color: inherit;
    text-decoration: none;
    border-left: .125rem solid transparent
}

.bd-toc nav a:hover,.bd-toc nav a.active {
    color: var(--bd-toc-color);
    border-left-color: var(--bd-toc-color)
}

.bd-toc nav a.active {
    font-weight: 500
}

.bd-toc nav a code {
    font: inherit
}

.bd-toc-toggle {
    display: flex;
    align-items: center
}

@media (max-width: 575.98px) {
    .bd-toc-toggle {
        justify-content:space-between;
        width: 100%
    }
}

@media (max-width: 767.98px) {
    .bd-toc-toggle {
        color:var(--bs-body-color);
        border: 1px solid var(--bs-border-color);
        border-radius: var(--bs-border-radius)
    }

    .bd-toc-toggle:hover,.bd-toc-toggle:focus,.bd-toc-toggle:active,.bd-toc-toggle[aria-expanded="true"] {
        color: var(--bd-violet);
        background-color: var(--bs-body-bg);
        border-color: var(--bd-violet)
    }

    .bd-toc-toggle:focus,.bd-toc-toggle[aria-expanded="true"] {
        box-shadow: 0 0 0 3px rgba(var(--bd-violet-rgb), 0.25)
    }
}

@media (max-width: 767.98px) {
    .bd-toc-collapse nav {
        padding:1.25rem 1.25rem 1.25rem 1rem;
        background-color: var(--bs-tertiary-bg);
        border: 1px solid var(--bs-border-color);
        border-radius: var(--bs-border-radius)
    }
}

@media (min-width: 768px) {
    .bd-toc-collapse {
        display:block !important
    }
}

.bd-footer a {
    color: var(--bs-body-color);
    text-decoration: none
}

.bd-footer a:hover,.bd-footer a:focus {
    color: var(--bs-link-hover-color);
    text-decoration: underline
}

.bd-code-snippet {
    margin: 0 -1.5rem 1rem;
    border: solid var(--bs-border-color);
    border-width: 1px 0
}

@media (min-width: 768px) {
    .bd-code-snippet {
        margin-right:0;
        margin-left: 0;
        border-width: 1px;
        border-radius: var(--bs-border-radius)
    }
}

.bd-example {
    --bd-example-padding: 1rem;
    position: relative;
    padding: var(--bd-example-padding);
    margin: 0 -1.5rem 1rem;
    border: solid var(--bs-border-color);
    border-width: 1px 0
}

.bd-example::after {
    display: block;
    clear: both;
    content: ""
}

@media (min-width: 768px) {
    .bd-example {
        --bd-example-padding: 1.5rem;
        margin-right: 0;
        margin-left: 0;
        border-width: 1px;
        border-radius: var(--bs-border-radius)
    }
}

.bd-example+p {
    margin-top: 2rem
}

.bd-example>.form-control+.form-control {
    margin-top: .5rem
}

.bd-example>.nav+.nav,.bd-example>.alert+.alert,.bd-example>.navbar+.navbar,.bd-example>.progress+.progress {
    margin-top: 1rem
}

.bd-example>.dropdown-menu {
    position: static;
    display: block
}

.bd-example>:last-child,.bd-example>nav:last-child .breadcrumb {
    margin-bottom: 0
}

.bd-example>hr:last-child {
    margin-bottom: 1rem
}

.bd-example>svg+svg,.bd-example>img+img {
    margin-left: .5rem
}

.bd-example>.btn,.bd-example>.btn-group {
    margin: .25rem .125rem
}

.bd-example>.btn-toolbar+.btn-toolbar {
    margin-top: .5rem
}

.bd-example>.list-group {
    max-width: 400px
}

.bd-example>[class*="list-group-horizontal"] {
    max-width: 100%
}

.bd-example .fixed-top,.bd-example .sticky-top {
    position: static;
    margin: calc(var(--bd-example-padding) * -1) calc(var(--bd-example-padding) * -1) var(--bd-example-padding)
}

.bd-example .fixed-bottom,.bd-example .sticky-bottom {
    position: static;
    margin: var(--bd-example-padding) calc(var(--bd-example-padding) * -1) calc(var(--bd-example-padding) * -1)
}

.bd-example .pagination {
    margin-bottom: 0
}

.bd-example-row [class^="col"],.bd-example-cols [class^="col"]>*,.bd-example-cssgrid [class*="grid"]>* {
    padding-top: .75rem;
    padding-bottom: .75rem;
    background-color: rgba(var(--bd-violet-rgb), 0.15);
    border: 1px solid rgba(var(--bd-violet-rgb), 0.3)
}

.bd-example-row .row+.row,.bd-example-cssgrid .grid+.grid {
    margin-top: 1rem
}

.bd-example-row-flex-cols .row {
    min-height: 10rem;
    background-color: rgba(var(--bd-violet-rgb), 0.15)
}

.bd-example-flex div:not(.vr) {
    background-color: rgba(var(--bd-violet-rgb), 0.15);
    border: 1px solid rgba(var(--bd-violet-rgb), 0.3)
}

.example-container {
    width: 800px;
    --bs-gutter-x: 1.5rem;
    --bs-gutter-y: 0;
    width: 100%;
    padding-right: calc(var(--bs-gutter-x) * .5);
    padding-left: calc(var(--bs-gutter-x) * .5);
    margin-right: auto;
    margin-left: auto
}

.example-row {
    --bs-gutter-x: 1.5rem;
    --bs-gutter-y: 0;
    display: flex;
    flex-wrap: wrap;
    margin-top: calc(-1 * var(--bs-gutter-y));
    margin-right: calc(-.5 * var(--bs-gutter-x));
    margin-left: calc(-.5 * var(--bs-gutter-x))
}

.example-content-main {
    flex-shrink: 0;
    width: 100%;
    max-width: 100%;
    padding-right: calc(var(--bs-gutter-x) * .5);
    padding-left: calc(var(--bs-gutter-x) * .5);
    margin-top: var(--bs-gutter-y)
}

@media (min-width: 576px) {
    .example-content-main {
        flex:0 0 auto;
        width: 50%
    }
}

@media (min-width: 992px) {
    .example-content-main {
        flex:0 0 auto;
        width: 66.666667%
    }
}

.example-content-secondary {
    flex-shrink: 0;
    width: 100%;
    max-width: 100%;
    padding-right: calc(var(--bs-gutter-x) * .5);
    padding-left: calc(var(--bs-gutter-x) * .5);
    margin-top: var(--bs-gutter-y)
}

@media (min-width: 576px) {
    .example-content-secondary {
        flex:0 0 auto;
        width: 50%
    }
}

@media (min-width: 992px) {
    .example-content-secondary {
        flex:0 0 auto;
        width: 33.333333%
    }
}

.bd-example-ratios .ratio {
    display: inline-block;
    width: 10rem;
    color: var(--bs-secondary-color);
    background-color: var(--bs-tertiary-bg);
    border: var(--bs-border-width) solid var(--bs-border-color)
}

.bd-example-ratios .ratio>div {
    display: flex;
    align-items: center;
    justify-content: center
}

.bd-example-ratios-breakpoint .ratio-4x3 {
    width: 16rem
}

@media (min-width: 768px) {
    .bd-example-ratios-breakpoint .ratio-4x3 {
        --bs-aspect-ratio: 50%
    }
}

.bd-example-offcanvas .offcanvas {
    position: static;
    display: block;
    height: 200px;
    visibility: visible;
    transform: translate(0)
}

.tooltip-demo a {
    white-space: nowrap
}

.tooltip-demo .btn {
    margin: .25rem .125rem
}

.custom-tooltip {
    --bs-tooltip-bg: var(--bd-violet-bg);
    --bs-tooltip-color: var(--bs-white)
}

.custom-popover {
    --bs-popover-max-width: 200px;
    --bs-popover-border-color: var(--bd-violet-bg);
    --bs-popover-header-bg: var(--bd-violet-bg);
    --bs-popover-header-color: var(--bs-white);
    --bs-popover-body-padding-x: 1rem;
    --bs-popover-body-padding-y: .5rem
}

.scrollspy-example {
    height: 200px;
    margin-top: .5rem;
    overflow: auto
}

.scrollspy-example-2 {
    height: 350px;
    overflow: auto
}

.simple-list-example-scrollspy .active {
    background-color: rgba(var(--bd-violet-rgb), 0.15)
}

.bd-example-border-utils [class^="border"] {
    display: inline-block;
    width: 5rem;
    height: 5rem;
    margin: .25rem;
    background-color: var(--bs-tertiary-bg)
}

.bd-example-rounded-utils [class*="rounded"] {
    margin: .25rem
}

.bd-example-position-utils {
    position: relative;
    padding: 2rem
}

.bd-example-position-utils .position-relative {
    height: 200px;
    background-color: var(--bs-tertiary-bg)
}

.bd-example-position-utils .position-absolute {
    width: 2rem;
    height: 2rem;
    background-color: var(--bs-body-color);
    border-radius: .375rem
}

.bd-example-position-examples::after {
    content: none
}

.bd-example-placeholder-cards::after {
    display: none
}

.bd-example-placeholder-cards .card {
    width: 18rem
}

.bd-example-toasts {
    min-height: 240px
}

.bd-example-zindex-levels {
    min-height: 15rem
}

.bd-example-zindex-levels>div {
    color: var(--bs-body-bg);
    background-color: var(--bd-violet);
    border: 1px solid var(--bd-purple)
}

.bd-example-zindex-levels>div>span {
    position: absolute;
    right: 5px;
    bottom: 0
}

.bd-example-zindex-levels>:nth-child(2) {
    top: 3rem;
    left: 3rem
}

.bd-example-zindex-levels>:nth-child(3) {
    top: 4.5rem;
    left: 4.5rem
}

.bd-example-zindex-levels>:nth-child(4) {
    top: 6rem;
    left: 6rem
}

.bd-example-zindex-levels>:nth-child(5) {
    top: 7.5rem;
    left: 7.5rem
}

.highlight {
    position: relative;
    padding: 0.75rem 1.5rem;
    background-color: var(--bd-pre-bg)
}

@media (min-width: 768px) {
    .highlight {
        padding:.75rem 1.25rem;
        border-radius: calc(var(--bs-border-radius) - 1px)
    }
}

@media (min-width: 992px) {
    .highlight pre {
        margin-right:1.875rem
    }
}

.highlight pre {
    padding: .25rem 0 .875rem;
    margin-top: .8125rem;
    margin-bottom: 0;
    overflow: overlay;
    white-space: pre;
    background-color: transparent;
    border: 0
}

.highlight pre code {
    font-size: inherit;
    color: var(--bs-body-color);
    word-wrap: normal
}

.bd-example-snippet .highlight pre {
    margin-right: 0
}

.highlight-toolbar {
    background-color: var(--bd-pre-bg)
}

.highlight-toolbar+.highlight {
    border-top-left-radius: 0;
    border-top-right-radius: 0
}

@media (min-width: 768px) {
    .bd-file-ref .highlight-toolbar {
        border-top-left-radius:calc(var(--bs-border-radius) - 1px);
        border-top-right-radius: calc(var(--bs-border-radius) - 1px)
    }
}

.bd-content .bd-code-snippet {
    margin-bottom: 1rem
}

.btn-bd-primary {
    --bs-btn-font-weight: 600;
    --bs-btn-color: var(--bs-white);
    --bs-btn-bg: var(--bd-violet-bg);
    --bs-btn-border-color: var(--bd-violet-bg);
    --bs-btn-hover-color: var(--bs-white);
    --bs-btn-hover-bg: #6528e0;
    --bs-btn-hover-border-color: #6528e0;
    --bs-btn-focus-shadow-rgb: var(--bd-violet-rgb);
    --bs-btn-active-color: var(--bs-btn-hover-color);
    --bs-btn-active-bg: #5a23c8;
    --bs-btn-active-border-color: #5a23c8
}

.btn-bd-accent {
    --bs-btn-font-weight: 600;
    --bs-btn-color: var(--bd-accent);
    --bs-btn-border-color: var(--bd-accent);
    --bs-btn-hover-color: var(--bd-dark);
    --bs-btn-hover-bg: var(--bd-accent);
    --bs-btn-hover-border-color: var(--bd-accent);
    --bs-btn-focus-shadow-rgb: var(--bd-accent-rgb);
    --bs-btn-active-color: var(--bs-btn-hover-color);
    --bs-btn-active-bg: var(--bs-btn-hover-bg);
    --bs-btn-active-border-color: var(--bs-btn-hover-border-color)
}

.btn-bd-light {
    --btn-custom-color: #9461fb;
    --bs-btn-color: var(--bs-gray-600);
    --bs-btn-border-color: var(--bs-border-color);
    --bs-btn-hover-color: var(--btn-custom-color);
    --bs-btn-hover-border-color: var(--btn-custom-color);
    --bs-btn-active-color: var(--btn-custom-color);
    --bs-btn-active-bg: var(--bs-white);
    --bs-btn-active-border-color: var(--btn-custom-color);
    --bs-btn-focus-border-color: var(--btn-custom-color);
    --bs-btn-focus-shadow-rgb: var(--bd-violet-rgb)
}

.bd-btn-lg {
    --bs-btn-border-radius: .5rem;
    padding: .8125rem 2rem
}

.bd-callout {
    --bs-link-color-rgb: var(--bd-callout-link);
    --bs-code-color: var(--bd-callout-code-color);
    padding: 1.25rem;
    margin-top: 1.25rem;
    margin-bottom: 1.25rem;
    color: var(--bd-callout-color, inherit);
    background-color: var(--bd-callout-bg, var(--bs-gray-100));
    border-left: 0.25rem solid var(--bd-callout-border, var(--bs-gray-300))
}

.bd-callout h4 {
    margin-bottom: .25rem
}

.bd-callout>:last-child {
    margin-bottom: 0
}

.bd-callout+.bd-callout {
    margin-top: -.25rem
}

.bd-callout .highlight {
    background-color: rgba(0,0,0,0.05)
}

.bd-callout-info {
    --bd-callout-color: var(--bs-info-text-emphasis);
    --bd-callout-bg: var(--bs-info-bg-subtle);
    --bd-callout-border: var(--bs-info-border-subtle)
}

.bd-callout-warning {
    --bd-callout-color: var(--bs-warning-text-emphasis);
    --bd-callout-bg: var(--bs-warning-bg-subtle);
    --bd-callout-border: var(--bs-warning-border-subtle)
}

.bd-callout-danger {
    --bd-callout-color: var(--bs-danger-text-emphasis);
    --bd-callout-bg: var(--bs-danger-bg-subtle);
    --bd-callout-border: var(--bs-danger-border-subtle)
}

.bd-brand-logos {
    color: #712cf9
}

.bd-brand-logos .inverse {
    color: #fff;
    background-color: #712cf9
}

.bd-brand-item+.bd-brand-item {
    border-top: 1px solid var(--bs-border-color)
}

@media (min-width: 768px) {
    .bd-brand-item+.bd-brand-item {
        border-top:0;
        border-left: 1px solid var(--bs-border-color)
    }
}

.color-swatches {
    margin: 0 -5px
}

.color-swatches .bd-purple {
    background-color: #4c0bce
}

.color-swatches .bd-purple-light {
    background-color: #d5c1fd
}

.color-swatches .bd-purple-lighter {
    background-color: #e5e1ea
}

.color-swatches .bd-gray {
    background-color: #f9f9f9
}

.color-swatch {
    width: 4rem;
    height: 4rem
}

@media (min-width: 768px) {
    .color-swatch {
        width:6rem;
        height: 6rem
    }
}

.swatch-blue {
    color: #fff;
    background-color: #0d6efd
}

.swatch-blue::after {
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding-left: 1rem;
    font-size: .75rem;
    line-height: 1.35;
    white-space: pre;
    content: "4.50" "\a" "4.50" "\a" "4.66";
    background-color: #0d6efd;
    background-image: linear-gradient(to bottom, transparent 0.25rem, #fff 0.25rem 0.75rem, transparent 0.75rem 1.25rem, #fff 1.25rem 1.75rem, transparent 1.75rem 2.25rem, #000 2.25rem 2.75rem, transparent 2.75rem);
    background-repeat: no-repeat;
    background-size: .5rem 100%
}

.swatch-indigo {
    color: #fff;
    background-color: #6610f2
}

.swatch-indigo::after {
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding-left: 1rem;
    font-size: .75rem;
    line-height: 1.35;
    white-space: pre;
    content: "7.18" "\a" "7.18" "\a" "2.92";
    background-color: #6610f2;
    background-image: linear-gradient(to bottom, transparent 0.25rem, #fff 0.25rem 0.75rem, transparent 0.75rem 1.25rem, #fff 1.25rem 1.75rem, transparent 1.75rem 2.25rem, #000 2.25rem 2.75rem, transparent 2.75rem);
    background-repeat: no-repeat;
    background-size: .5rem 100%
}

.swatch-purple {
    color: #fff;
    background-color: #6f42c1
}

.swatch-purple::after {
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding-left: 1rem;
    font-size: .75rem;
    line-height: 1.35;
    white-space: pre;
    content: "6.51" "\a" "6.51" "\a" "3.22";
    background-color: #6f42c1;
    background-image: linear-gradient(to bottom, transparent 0.25rem, #fff 0.25rem 0.75rem, transparent 0.75rem 1.25rem, #fff 1.25rem 1.75rem, transparent 1.75rem 2.25rem, #000 2.25rem 2.75rem, transparent 2.75rem);
    background-repeat: no-repeat;
    background-size: .5rem 100%
}

.swatch-pink {
    color: #fff;
    background-color: #d63384
}

.swatch-pink::after {
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding-left: 1rem;
    font-size: .75rem;
    line-height: 1.35;
    white-space: pre;
    content: "4.50" "\a" "4.50" "\a" "4.66";
    background-color: #d63384;
    background-image: linear-gradient(to bottom, transparent 0.25rem, #fff 0.25rem 0.75rem, transparent 0.75rem 1.25rem, #fff 1.25rem 1.75rem, transparent 1.75rem 2.25rem, #000 2.25rem 2.75rem, transparent 2.75rem);
    background-repeat: no-repeat;
    background-size: .5rem 100%
}

.swatch-red {
    color: #fff;
    background-color: #dc3545
}

.swatch-red::after {
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding-left: 1rem;
    font-size: .75rem;
    line-height: 1.35;
    white-space: pre;
    content: "4.52" "\a" "4.52" "\a" "4.63";
    background-color: #dc3545;
    background-image: linear-gradient(to bottom, transparent 0.25rem, #fff 0.25rem 0.75rem, transparent 0.75rem 1.25rem, #fff 1.25rem 1.75rem, transparent 1.75rem 2.25rem, #000 2.25rem 2.75rem, transparent 2.75rem);
    background-repeat: no-repeat;
    background-size: .5rem 100%
}

.swatch-orange {
    color: #000;
    background-color: #fd7e14
}

.swatch-orange::after {
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding-left: 1rem;
    font-size: .75rem;
    line-height: 1.35;
    white-space: pre;
    content: "8.17" "\a" "2.57" "\a" "8.17";
    background-color: #fd7e14;
    background-image: linear-gradient(to bottom, transparent 0.25rem, #000 0.25rem 0.75rem, transparent 0.75rem 1.25rem, #fff 1.25rem 1.75rem, transparent 1.75rem 2.25rem, #000 2.25rem 2.75rem, transparent 2.75rem);
    background-repeat: no-repeat;
    background-size: .5rem 100%
}

.swatch-yellow {
    color: #000;
    background-color: #ffc107
}

.swatch-yellow::after {
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding-left: 1rem;
    font-size: .75rem;
    line-height: 1.35;
    white-space: pre;
    content: "12.8" "\a" "1.63" "\a" "12.8";
    background-color: #ffc107;
    background-image: linear-gradient(to bottom, transparent 0.25rem, #000 0.25rem 0.75rem, transparent 0.75rem 1.25rem, #fff 1.25rem 1.75rem, transparent 1.75rem 2.25rem, #000 2.25rem 2.75rem, transparent 2.75rem);
    background-repeat: no-repeat;
    background-size: .5rem 100%
}

.swatch-green {
    color: #fff;
    background-color: #198754
}

.swatch-green::after {
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding-left: 1rem;
    font-size: .75rem;
    line-height: 1.35;
    white-space: pre;
    content: "4.53" "\a" "4.53" "\a" "4.63";
    background-color: #198754;
    background-image: linear-gradient(to bottom, transparent 0.25rem, #fff 0.25rem 0.75rem, transparent 0.75rem 1.25rem, #fff 1.25rem 1.75rem, transparent 1.75rem 2.25rem, #000 2.25rem 2.75rem, transparent 2.75rem);
    background-repeat: no-repeat;
    background-size: .5rem 100%
}

.swatch-teal {
    color: #000;
    background-color: #20c997
}

.swatch-teal::after {
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding-left: 1rem;
    font-size: .75rem;
    line-height: 1.35;
    white-space: pre;
    content: "9.86" "\a" "2.12" "\a" "9.86";
    background-color: #20c997;
    background-image: linear-gradient(to bottom, transparent 0.25rem, #000 0.25rem 0.75rem, transparent 0.75rem 1.25rem, #fff 1.25rem 1.75rem, transparent 1.75rem 2.25rem, #000 2.25rem 2.75rem, transparent 2.75rem);
    background-repeat: no-repeat;
    background-size: .5rem 100%
}

.swatch-cyan {
    color: #000;
    background-color: #0dcaf0
}

.swatch-cyan::after {
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding-left: 1rem;
    font-size: .75rem;
    line-height: 1.35;
    white-space: pre;
    content: "10.7" "\a" "1.95" "\a" "10.7";
    background-color: #0dcaf0;
    background-image: linear-gradient(to bottom, transparent 0.25rem, #000 0.25rem 0.75rem, transparent 0.75rem 1.25rem, #fff 1.25rem 1.75rem, transparent 1.75rem 2.25rem, #000 2.25rem 2.75rem, transparent 2.75rem);
    background-repeat: no-repeat;
    background-size: .5rem 100%
}

.swatch-black {
    color: #fff;
    background-color: #000
}

.swatch-black::after {
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding-left: 1rem;
    font-size: .75rem;
    line-height: 1.35;
    white-space: pre;
    content: "21" "\a" "21" "\a" "1";
    background-color: #000;
    background-image: linear-gradient(to bottom, transparent 0.25rem, #fff 0.25rem 0.75rem, transparent 0.75rem 1.25rem, #fff 1.25rem 1.75rem, transparent 1.75rem 2.25rem, #000 2.25rem 2.75rem, transparent 2.75rem);
    background-repeat: no-repeat;
    background-size: .5rem 100%
}

.swatch-white {
    color: #000;
    background-color: #fff
}

.swatch-white::after {
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding-left: 1rem;
    font-size: .75rem;
    line-height: 1.35;
    white-space: pre;
    content: "21" "\a" "1" "\a" "21";
    background-color: #fff;
    background-image: linear-gradient(to bottom, transparent 0.25rem, #000 0.25rem 0.75rem, transparent 0.75rem 1.25rem, #fff 1.25rem 1.75rem, transparent 1.75rem 2.25rem, #000 2.25rem 2.75rem, transparent 2.75rem);
    background-repeat: no-repeat;
    background-size: .5rem 100%
}

.swatch-gray {
    color: #fff;
    background-color: #6c757d
}

.swatch-gray::after {
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding-left: 1rem;
    font-size: .75rem;
    line-height: 1.35;
    white-space: pre;
    content: "4.68" "\a" "4.68" "\a" "4.47";
    background-color: #6c757d;
    background-image: linear-gradient(to bottom, transparent 0.25rem, #fff 0.25rem 0.75rem, transparent 0.75rem 1.25rem, #fff 1.25rem 1.75rem, transparent 1.75rem 2.25rem, #000 2.25rem 2.75rem, transparent 2.75rem);
    background-repeat: no-repeat;
    background-size: .5rem 100%
}

.swatch-gray-dark {
    color: #fff;
    background-color: #343a40
}

.swatch-gray-dark::after {
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding-left: 1rem;
    font-size: .75rem;
    line-height: 1.35;
    white-space: pre;
    content: "11.5" "\a" "11.5" "\a" "1.82";
    background-color: #343a40;
    background-image: linear-gradient(to bottom, transparent 0.25rem, #fff 0.25rem 0.75rem, transparent 0.75rem 1.25rem, #fff 1.25rem 1.75rem, transparent 1.75rem 2.25rem, #000 2.25rem 2.75rem, transparent 2.75rem);
    background-repeat: no-repeat;
    background-size: .5rem 100%
}

.swatch-gray-500 {
    color: #000;
    background-color: #adb5bd
}

.swatch-gray-500::after {
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding-left: 1rem;
    font-size: .75rem;
    line-height: 1.35;
    white-space: pre;
    content: "10.1" "\a" "2.07" "\a" "10.1";
    background-color: #adb5bd;
    background-image: linear-gradient(to bottom, transparent 0.25rem, #000 0.25rem 0.75rem, transparent 0.75rem 1.25rem, #fff 1.25rem 1.75rem, transparent 1.75rem 2.25rem, #000 2.25rem 2.75rem, transparent 2.75rem);
    background-repeat: no-repeat;
    background-size: .5rem 100%
}

.bd-blue-100 {
    color: #000;
    background-color: #cfe2ff
}

.bd-blue-200 {
    color: #000;
    background-color: #9ec5fe
}

.bd-blue-300 {
    color: #000;
    background-color: #6ea8fe
}

.bd-blue-400 {
    color: #000;
    background-color: #3d8bfd
}

.bd-blue-500 {
    color: #fff;
    background-color: #0d6efd
}

.bd-blue-600 {
    color: #fff;
    background-color: #0a58ca
}

.bd-blue-700 {
    color: #fff;
    background-color: #084298
}

.bd-blue-800 {
    color: #fff;
    background-color: #052c65
}

.bd-blue-900 {
    color: #fff;
    background-color: #031633
}

.bd-indigo-100 {
    color: #000;
    background-color: #e0cffc
}

.bd-indigo-200 {
    color: #000;
    background-color: #c29ffa
}

.bd-indigo-300 {
    color: #000;
    background-color: #a370f7
}

.bd-indigo-400 {
    color: #fff;
    background-color: #8540f5
}

.bd-indigo-500 {
    color: #fff;
    background-color: #6610f2
}

.bd-indigo-600 {
    color: #fff;
    background-color: #520dc2
}

.bd-indigo-700 {
    color: #fff;
    background-color: #3d0a91
}

.bd-indigo-800 {
    color: #fff;
    background-color: #290661
}

.bd-indigo-900 {
    color: #fff;
    background-color: #140330
}

.bd-purple-100 {
    color: #000;
    background-color: #e2d9f3
}

.bd-purple-200 {
    color: #000;
    background-color: #c5b3e6
}

.bd-purple-300 {
    color: #000;
    background-color: #a98eda
}

.bd-purple-400 {
    color: #000;
    background-color: #8c68cd
}

.bd-purple-500 {
    color: #fff;
    background-color: #6f42c1
}

.bd-purple-600 {
    color: #fff;
    background-color: #59359a
}

.bd-purple-700 {
    color: #fff;
    background-color: #432874
}

.bd-purple-800 {
    color: #fff;
    background-color: #2c1a4d
}

.bd-purple-900 {
    color: #fff;
    background-color: #160d27
}

.bd-pink-100 {
    color: #000;
    background-color: #f7d6e6
}

.bd-pink-200 {
    color: #000;
    background-color: #efadce
}

.bd-pink-300 {
    color: #000;
    background-color: #e685b5
}

.bd-pink-400 {
    color: #000;
    background-color: #de5c9d
}

.bd-pink-500 {
    color: #fff;
    background-color: #d63384
}

.bd-pink-600 {
    color: #fff;
    background-color: #ab296a
}

.bd-pink-700 {
    color: #fff;
    background-color: #801f4f
}

.bd-pink-800 {
    color: #fff;
    background-color: #561435
}

.bd-pink-900 {
    color: #fff;
    background-color: #2b0a1a
}

.bd-red-100 {
    color: #000;
    background-color: #f8d7da
}

.bd-red-200 {
    color: #000;
    background-color: #f1aeb5
}

.bd-red-300 {
    color: #000;
    background-color: #ea868f
}

.bd-red-400 {
    color: #000;
    background-color: #e35d6a
}

.bd-red-500 {
    color: #fff;
    background-color: #dc3545
}

.bd-red-600 {
    color: #fff;
    background-color: #b02a37
}

.bd-red-700 {
    color: #fff;
    background-color: #842029
}

.bd-red-800 {
    color: #fff;
    background-color: #58151c
}

.bd-red-900 {
    color: #fff;
    background-color: #2c0b0e
}

.bd-orange-100 {
    color: #000;
    background-color: #ffe5d0
}

.bd-orange-200 {
    color: #000;
    background-color: #fecba1
}

.bd-orange-300 {
    color: #000;
    background-color: #feb272
}

.bd-orange-400 {
    color: #000;
    background-color: #fd9843
}

.bd-orange-500 {
    color: #000;
    background-color: #fd7e14
}

.bd-orange-600 {
    color: #000;
    background-color: #ca6510
}

.bd-orange-700 {
    color: #fff;
    background-color: #984c0c
}

.bd-orange-800 {
    color: #fff;
    background-color: #653208
}

.bd-orange-900 {
    color: #fff;
    background-color: #331904
}

.bd-yellow-100 {
    color: #000;
    background-color: #fff3cd
}

.bd-yellow-200 {
    color: #000;
    background-color: #ffe69c
}

.bd-yellow-300 {
    color: #000;
    background-color: #ffda6a
}

.bd-yellow-400 {
    color: #000;
    background-color: #ffcd39
}

.bd-yellow-500 {
    color: #000;
    background-color: #ffc107
}

.bd-yellow-600 {
    color: #000;
    background-color: #cc9a06
}

.bd-yellow-700 {
    color: #000;
    background-color: #997404
}

.bd-yellow-800 {
    color: #fff;
    background-color: #664d03
}

.bd-yellow-900 {
    color: #fff;
    background-color: #332701
}

.bd-green-100 {
    color: #000;
    background-color: #d1e7dd
}

.bd-green-200 {
    color: #000;
    background-color: #a3cfbb
}

.bd-green-300 {
    color: #000;
    background-color: #75b798
}

.bd-green-400 {
    color: #000;
    background-color: #479f76
}

.bd-green-500 {
    color: #fff;
    background-color: #198754
}

.bd-green-600 {
    color: #fff;
    background-color: #146c43
}

.bd-green-700 {
    color: #fff;
    background-color: #0f5132
}

.bd-green-800 {
    color: #fff;
    background-color: #0a3622
}

.bd-green-900 {
    color: #fff;
    background-color: #051b11
}

.bd-teal-100 {
    color: #000;
    background-color: #d2f4ea
}

.bd-teal-200 {
    color: #000;
    background-color: #a6e9d5
}

.bd-teal-300 {
    color: #000;
    background-color: #79dfc1
}

.bd-teal-400 {
    color: #000;
    background-color: #4dd4ac
}

.bd-teal-500 {
    color: #000;
    background-color: #20c997
}

.bd-teal-600 {
    color: #000;
    background-color: #1aa179
}

.bd-teal-700 {
    color: #fff;
    background-color: #13795b
}

.bd-teal-800 {
    color: #fff;
    background-color: #0d503c
}

.bd-teal-900 {
    color: #fff;
    background-color: #06281e
}

.bd-cyan-100 {
    color: #000;
    background-color: #cff4fc
}

.bd-cyan-200 {
    color: #000;
    background-color: #9eeaf9
}

.bd-cyan-300 {
    color: #000;
    background-color: #6edff6
}

.bd-cyan-400 {
    color: #000;
    background-color: #3dd5f3
}

.bd-cyan-500 {
    color: #000;
    background-color: #0dcaf0
}

.bd-cyan-600 {
    color: #000;
    background-color: #0aa2c0
}

.bd-cyan-700 {
    color: #fff;
    background-color: #087990
}

.bd-cyan-800 {
    color: #fff;
    background-color: #055160
}

.bd-cyan-900 {
    color: #fff;
    background-color: #032830
}

.bd-gray-100 {
    color: #000;
    background-color: #f8f9fa
}

.bd-gray-200 {
    color: #000;
    background-color: #e9ecef
}

.bd-gray-300 {
    color: #000;
    background-color: #dee2e6
}

.bd-gray-400 {
    color: #000;
    background-color: #ced4da
}

.bd-gray-500 {
    color: #000;
    background-color: #adb5bd
}

.bd-gray-600 {
    color: #fff;
    background-color: #6c757d
}

.bd-gray-700 {
    color: #fff;
    background-color: #495057
}

.bd-gray-800 {
    color: #fff;
    background-color: #343a40
}

.bd-gray-900 {
    color: #fff;
    background-color: #212529
}

.bd-white {
    color: #000;
    background-color: #fff
}

.bd-black {
    color: #fff;
    background-color: #000
}

.bd-clipboard,.bd-edit {
    position: relative;
    display: none;
    float: right
}

.bd-clipboard+.highlight,.bd-edit+.highlight {
    margin-top: 0
}

@media (min-width: 768px) {
    .bd-clipboard,.bd-edit {
        display:block
    }
}

.btn-clipboard,.btn-edit {
    display: block;
    padding: .5em;
    line-height: 1;
    color: var(--bs-body-color);
    background-color: var(--bd-pre-bg);
    border: 0;
    border-radius: .25rem
}

.btn-clipboard:hover,.btn-edit:hover {
    color: var(--bs-link-hover-color)
}

.btn-clipboard:focus,.btn-edit:focus {
    z-index: 3
}

.btn-clipboard {
    position: relative;
    z-index: 2;
    margin-top: 1.25rem;
    margin-right: .75rem
}

.bd-placeholder-img {
    font-size: 1.125rem;
    -webkit-user-select: none;
    -moz-user-select: none;
    user-select: none;
    text-anchor: middle
}

.bd-placeholder-img-lg {
    font-size: calc(1.475rem + 2.7vw)
}

@media (min-width: 1200px) {
    .bd-placeholder-img-lg {
        font-size:3.5rem
    }
}

main a,main button,main input,main select,main textarea,main h2,main h3,main h4,main [tabindex="0"] {
    scroll-margin-top: 80px;
    scroll-margin-bottom: 100px
}

:root,[data-bs-theme="light"] {
    --base02: #c8c8fa;
    --base03: #565c64;
    --base04: #666;
    --base05: #333;
    --base06: #fff;
    --base07: #13795b;
    --base08: #c6303e;
    --base09: #087990;
    --base0A: #6f42c1;
    --base0B: #084298;
    --base0C: #084298;
    --base0D: #6f42c1;
    --base0E: #ab296a;
    --base0F: #333
}

[data-bs-theme="dark"] {
    --base02: #3e4451;
    --base03: #868e96;
    --base04: #868e96;
    --base05: #abb2bf;
    --base06: #b6bdca;
    --base07: #feb272;
    --base08: #6edff6;
    --base09: #feb272;
    --base0A: #ffe69c;
    --base0B: #79dfc1;
    --base0C: #79dfc1;
    --base0D: #6ea8fe;
    --base0E: #c29ffa;
    --base0F: #ea868f
}

[data-bs-theme="dark"] .language-diff .gd {
    color: #e35d6a
}

[data-bs-theme="dark"] .language-diff .gi {
    color: #479f76
}

.hl {
    background-color: var(--base02)
}

.c {
    color: var(--base03)
}

.err {
    color: var(--base08)
}

.k {
    color: var(--base0E)
}

.l {
    color: var(----base09)
}

.n {
    color: var(--base08)
}

.o {
    color: var(--base05)
}

.p {
    color: var(--base05)
}

.cm {
    color: var(--base04)
}

.cp {
    color: var(--base08)
}

.c1 {
    color: var(--base03)
}

.cs {
    color: var(--base04)
}

.gd {
    color: var(--base08)
}

.ge {
    font-style: italic
}

.gh {
    font-weight: 600;
    color: var(--base0A)
}

.gi {
    color: var(--bs-success)
}

.gp {
    font-weight: 600;
    color: var(--base04)
}

.gs {
    font-weight: 600
}

.gu {
    font-weight: 600;
    color: var(--base0C)
}

.kc {
    color: var(--base0E)
}

.kd {
    color: var(--base0E)
}

.kn {
    color: var(--base0C)
}

.kp {
    color: var(--base0E)
}

.kr {
    color: var(--base0E)
}

.kt {
    color: var(--base0A)
}

.ld {
    color: var(--base0C)
}

.m {
    color: var(--base09)
}

.s {
    color: var(--base0C)
}

.na {
    color: var(--base0A)
}

.nb {
    color: var(--base05)
}

.nc {
    color: var(--base07)
}

.no {
    color: var(--base08)
}

.nd {
    color: var(--base07)
}

.ni {
    color: var(--base08)
}

.ne {
    color: var(--base08)
}

.nf {
    color: var(--base0B)
}

.nl {
    color: var(--base05)
}

.nn {
    color: var(--base0A)
}

.nx {
    color: var(--base0A)
}

.py {
    color: var(--base08)
}

.nt {
    color: var(--base08)
}

.nv {
    color: var(--base08)
}

.ow {
    color: var(--base0C)
}

.w {
    color: #fff
}

.mf {
    color: var(--base09)
}

.mh {
    color: var(--base09)
}

.mi {
    color: var(--base09)
}

.mo {
    color: var(--base09)
}

.sb {
    color: var(--base0C)
}

.sc {
    color: #fff
}

.sd {
    color: var(--base04)
}

.s2 {
    color: var(--base0C)
}

.se {
    color: var(--base09)
}

.sh {
    color: var(--base0C)
}

.si {
    color: var(--base09)
}

.sx {
    color: var(--base0C)
}

.sr {
    color: var(--base0C)
}

.s1 {
    color: var(--base0C)
}

.ss {
    color: var(--base0C)
}

.bp {
    color: var(--base05)
}

.vc {
    color: var(--base08)
}

.vg {
    color: var(--base08)
}

.vi {
    color: var(--base08)
}

.il {
    color: var(--base09)
}

.m+.o {
    color: var(--base03)
}

.language-sh .c {
    color: var(--base03)
}

.chroma .language-bash .line::before,.chroma .language-sh .line::before {
    color: var(--base03);
    content: "$ ";
    -webkit-user-select: none;
    -moz-user-select: none;
    user-select: none
}

.chroma .language-powershell::before {
    color: var(--base0C);
    content: "PM> ";
    -webkit-user-select: none;
    -moz-user-select: none;
    user-select: none
}

.anchor-link {
    padding: 0 .175rem;
    font-weight: 400;
    color: rgba(13,110,253,0.5);
    text-decoration: none;
    opacity: 0;
    transition: color 0.15s ease-in-out,opacity 0.15s ease-in-out
}

@media (prefers-reduced-motion: reduce) {
    .anchor-link {
        transition: none
    }
}

.anchor-link::after {
    content: "#"
}

.anchor-link:focus,.anchor-link:hover,:hover>.anchor-link,:target>.anchor-link {
    color: #0d6efd;
    text-decoration: none;
    opacity: 1
}

</style>
<link rel="icon" type="image/x-icon" href="./favicon.ico">
<style>
  .insight-card .number {
      font-size: 2.5rem;
      /* font-weight: bold;*/
      color: #ffffff; 
    }
    .insight-card .title {
      font-size: 1rem;
      color: #d55a90 ;
    }
</style>
<!-- chatbot css-->
 <style>
     .chat-container {
            height: 65vh;
            overflow-y: auto;
            padding: 1.5rem;
            margin-bottom: 1rem;
            scroll-behavior: smooth;
        }

        .message {
            margin-bottom: 1rem;
            padding: 1rem;
            border-radius: 1rem;
            max-width: 85%;
            position: relative;
            animation: fadeIn 0.3s ease-in-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .ai-message {
            background-color: #6a32ee;
            color: var(--text-primary);
            margin-right: auto;
            border-bottom-left-radius: 0.25rem;
        }

        .human-message {
            background-color: var(--primary-color);
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 0.25rem;
        }

        .insight-card {
            margin-bottom: 1.5rem;
        }

        .insight-card h5 {
            color: var(--text-primary);
            font-weight: 600;
            margin-bottom: 1rem;
        }

        .insight-item {
            padding: 0.75rem;
            border-radius: 0.5rem;
            background-color: #f8fafc;
            margin-bottom: 0.75rem;
            transition: background-color 0.2s;
        }

        .insight-item:hover {
            background-color: #f1f5f9;
        }

        .insight-item strong {
            color: var(--primary-color);
            font-weight: 600;
        }

        .input-group {
            /* background: white; */
            border-radius: 0.75rem;
            padding: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .form-control {
            border: none;
            padding: 0.75rem 1rem;
            font-size: 1rem;
            background: transparent;
            color: var(--text-primary);
        }

        .form-control:focus {
            box-shadow: none;
            outline: none;
        }

        .btn-primary {
            background-color: var(--primary-color);
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-weight: 500;
            transition: background-color 0.2s;
        }

        .btn-primary:hover {
            background-color: var(--secondary-color);
        }

        .spinner-border {
            width: 1.5rem;
            height: 1.5rem;
            border-width: 0.2rem;
            display: none;
        }

        .spinner-border.active {
            display: inline-block;
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
        }

        ::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 3px;
        }

        ::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 3px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
        }

        /* Animations */
        .fade-in {
            animation: fadeIn 0.3s ease-in-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .chat-container {
                height: 50vh;
            }
            
            .message {
                max-width: 90%;
            }
        }
 </style>
    <title>NewsK | AI News Recommendation</title>
  </head>
  <body>
      <!-- Header -->
    <nav class="navbar navbar-expand-lg bd-navbar sticky-top">
      <nav class="container-xxl bd-gutter flex-wrap flex-lg-nowrap" aria-label="Main navigation">
        <div class="d-lg-none" style="width: 4.25rem;"></div>
      <a class="navbar-brand p-0 me-0 me-lg-2" href="/" aria-label="Bootstrap">
        <img src="NewsK-logo.png" height="32" class="white-image">
      </a>
      <div class="offcanvas-lg offcanvas-end flex-grow-1" tabindex="-1" id="bdNavbar" aria-labelledby="bdNavbarOffcanvasLabel" data-bs-scroll="true">
        <div class="offcanvas-header px-4 pb-0">
          <h5 class="offcanvas-title text-white" id="bdNavbarOffcanvasLabel">Bootstrap</h5>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="offcanvas" aria-label="Close" data-bs-target="#bdNavbar"></button>
        </div>
        <div class="offcanvas-body p-4 pt-0 p-lg-0">
          <hr class="d-lg-none text-white-50">
          <hr class="d-lg-none text-white-50">
        </div>
      </div>
    </nav>
    </nav>
    <!-- Content -->
    <div class="bd-masthead mb-3" id="content" style="min-height: 400px;">
      <div class="container mt-3">
        <h3><i class="fas fa-robot"></i> NewsK AI Advisor</h3>
        <!-- Ai Chatbot-->
        <div class="row g-4">
            <div class="col-md-4">
                <div class="card insight-card mb-4 fade-in" id="analysisCard" style="display: none; border-radius: 20px" >
                    <div class="card-body">
                        <h5><i class="fas fa-chart-bar me-2"></i>Article Insights</h5>
                        <div class="insight-item">
                            <strong><i class="fas fa-file-alt me-2"></i>Summary:</strong>
                            <p id="articleSummary" class="mb-0 mt-2"></p>
                        </div>
                        <div class="insight-item">
                            <strong><i class="fas fa-folder me-2"></i>Category:</strong>
                            <p id="articleCategory" class="mb-0 mt-2"></p>
                        </div>
                        <div class="insight-item">
                            <strong><i class="fas fa-heart me-2"></i>Sentiment:</strong>
                            <p id="articleSentiment" class="mb-0 mt-2"></p>
                        </div>
                        <div class="insight-item">
                            <strong><i class="fas fa-tags me-2"></i>Keywords:</strong>
                            <p id="articleKeywords" class="mb-0 mt-2"></p>
                        </div>
                    </div>
                </div>
                
                <div class="card insight-card fade-in" style="border-radius: 20px">
                    <div class="card-body">
                        <h5><i class="fas fa-cog me-2"></i>Settings</h5>
                        <div class="mb-3">
                            <input type="text" id="urlInput" class="form-control" 
                                   placeholder="Enter article URL">
                        </div>
                        <button onclick="processArticle()" class="btn btn-warning w-100 mb-3">
                            <i class="fas fa-sync-alt me-2"></i>Process Article
                        </button>
                        <div class="text-center">
                            <div id="loadingSpinner" class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>
                        <small class="text-muted">
                            <i class="fas fa-info-circle me-1"></i>
                            Provide a URL to analyze an online article
                        </small>
                    </div>
                </div>
            </div>
            
            <div class="col-md-8">
                <div class="card h-100" style="border-radius: 20px">
                    <div class="card-body p-0 d-flex flex-column">
                        <div id="chatContainer" class="chat-container">
                            <div class="message ai-message fade-in">
                                <i class="fas fa-robot me-2"></i>Hello! I'm your NewsK AI Advisor. 
                                How can I help you analyze articles today?
                            </div>
                        </div>
                        
                        <div class="p-3">
                            <div class="input-group">
                                <input type="text" id="userInput" class="form-control" 
                                       placeholder="Ask me anything about the article...">
                                <button class="btn btn-warning" onclick="sendMessage()">
                                    <i class="fas fa-paper-plane"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
      </div>
  </div>
      </div>
      </div>
    </div>
  </div>
    <!-- Chart.js Library -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Bootstrap JS and dependencies (Popper.js and Bootstrap JS) -->
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.7/dist/umd/popper.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.min.js"></script>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        let vectorStoreReady = false;
        let chatHistory = [];

        function showSpinner() {
            document.getElementById('loadingSpinner').classList.add('active');
        }

        function hideSpinner() {
            document.getElementById('loadingSpinner').classList.remove('active');
        }

        function processArticle() {
            const url = document.getElementById('urlInput').value;
            if (!url) {
                showToast('Please enter a valid URL');
                return;
            }

            showSpinner();
            addMessage('Processing article... This may take a moment. ⏳', 'ai');

            $.ajax({
                url: '/process_article',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ url: url }),
                success: function(response) {
                    hideSpinner();
                    if (response.success) {
                        vectorStoreReady = true;
                        addMessage('Article processed successfully! 🎉 You can now ask questions about it.', 'ai');
                        
                        const analysisCard = document.getElementById('analysisCard');
                        analysisCard.style.display = 'block';
                        analysisCard.classList.add('fade-in');
                        
                        document.getElementById('articleSummary').textContent = response.analysis.summary || '';
                        document.getElementById('articleCategory').textContent = response.analysis.category || '';
                        document.getElementById('articleSentiment').textContent = response.analysis.sentiment || '';
                        document.getElementById('articleKeywords').textContent = response.analysis.keywords || '';
                    } else {
                        addMessage('Failed to process article. Please check the URL and try again. ❌', 'ai');
                    }
                },
                error: function() {
                    hideSpinner();
                    addMessage('Error processing article. Please try again. ❌', 'ai');
                }
            });
        }

        function sendMessage() {
            if (!vectorStoreReady) {
                showToast('Please process an article first');
                return;
            }

            const userInput = document.getElementById('userInput');
            const message = userInput.value.trim();
            if (!message) return;

            addMessage(message, 'human');
            userInput.value = '';

            $.ajax({
                url: '/chat',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ 
                    message: message,
                    chat_history: chatHistory
                }),
                beforeSend: function() {
                    showSpinner();
                },
                success: function(response) {
                    hideSpinner();
                    addMessage(response.response, 'ai');
                },
                error: function() {
                    hideSpinner();
                    addMessage('Error generating response. Please try again. ❌', 'ai');
                }
            });
        }

        function addMessage(message, sender) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message', `${sender}-message`, 'fade-in');
            
            if (sender === 'ai') {
                messageDiv.innerHTML = `<i class="fas fa-robot me-2"></i>${message}`;
            } else {
                messageDiv.innerHTML = `<i class="fas fa-user me-2"></i>${message}`;
            }
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            chatHistory.push({"role": sender, "content": message});
        }

        function showToast(message) {
            alert(message);
        }

        document.getElementById('userInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
  </body>
</html>
"""

# Configure device for Apple Silicon if available
device = "mps" if torch.backends.mps.is_available() else "cpu"

def initialize_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': device},
        encode_kwargs={'device': device, 'batch_size': 32}
    )

def get_vectorstore_from_url(url):
    try:
        loader = WebBaseLoader(url)
        document = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len
        )
        document_chunks = text_splitter.split_documents(document)
        embeddings = initialize_embeddings()
        
        vector_store = FAISS.from_documents(
            document_chunks, 
            embeddings
        )
        return vector_store, document
    except Exception as e:
        print(f"Error creating vector store: {str(e)}")
        return None, None

def get_llm():
    try:
        return Ollama(
            model="llama3:latest",
            temperature=0.7,
            num_ctx=4096,
            num_gpu=1,
            num_thread=4
        )
    except Exception as e:
        print(f"Error initializing LLM: {str(e)}")
        return None

def get_context_retriever_chain(vector_store, lang):
    llm = get_llm()
    if not llm:
        return None
        
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 3}
    )
    
    # Add language instructions in the prompt
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("user", f"Given the article we processed, provide information and insights based on its content. Respond in {lang}.")
    ])
    
    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
    return retriever_chain

def get_conversational_rag_chain(retriever_chain, lang):
    llm = get_llm()
    if not llm or not retriever_chain:
        return None
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are a helpful AI assistant analyzing articles. Provide relevant, fact-based answers derived from the article content. Respond in {lang}.\n\n{{context}}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
    ])
    
    stuff_documents_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever_chain, stuff_documents_chain)

def analyze_article_content(doc_text, lang):
    llm = get_llm()
    if llm is None:
        return {"summary": "", "category": "", "sentiment": "", "keywords": ""}

    # Updated prompt to ensure the response is in the detected language
    prompt = (
        f"You are a helpful AI news assistant analyzing the content of an article. Respond in {lang}.\n"
        "Return a JSON object with the following fields:\n\n"
        "summary: A concise summary of the article.\n"
        "category: The main category or topic of the article (Politics, Finance, Technology, Religion, Culture, Medical, etc.).\n"
        "sentiment: A single word describing the overall sentiment (positive, negative, or neutral).\n"
        "keywords: A list of the most important words or phrases capturing the article's main ideas.\n\n"
        "Your response must be strictly valid JSON with no additional commentary."
    )

    response = llm.invoke([HumanMessage(content=prompt + "\n\n" + doc_text)])
    text = response.strip()

    # Attempt JSON parsing with fallback
    try:
        data = json.loads(text)
    except:
        import re
        json_pattern = re.compile(r'\{(?:[^{}]|(?R))*\}', re.DOTALL)
        match = json_pattern.search(text)
        if match:
            try:
                data = json.loads(match.group(0))
            except:
                data = {}
        else:
            data = {}

    # Ensure all keys exist
    for key in ["summary", "category", "sentiment", "keywords"]:
        if key not in data:
            data[key] = ""

    # If sentiment is an object, flatten it to string
    if isinstance(data["sentiment"], dict):
        sentiment_value = data["sentiment"].get("value", "")
        data["sentiment"] = sentiment_value if sentiment_value else "neutral"

    # If keywords is a list, convert to comma-separated string
    if isinstance(data["keywords"], list):
        data["keywords"] = ", ".join(data["keywords"])

    return data

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/process_article', methods=['POST'])
def process_article():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'success': False, 'error': 'No URL provided'})
    
    vector_store, document = get_vectorstore_from_url(url)
    if vector_store:
        app.vector_store = vector_store
        
        full_text = document[0].page_content if document else ""
        
        # Detect language code
        try:
            lang_code = detect(full_text)
        except LangDetectException:
            lang_code = "ar"  # Default fallback

        # Map language code to full language name
        lang_map = {
            "ar": "Arabic",
            "en": "English",
            "fr": "French",
            "de": "German",
            "es": "Spanish",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "zh-cn": "Chinese (Simplified)",
            "zh-tw": "Chinese (Traditional)",
            "ja": "Japanese",
            "ko": "Korean",
            "nl": "Dutch",
            "sv": "Swedish",
            "no": "Norwegian",
            "fi": "Finnish",
            "da": "Danish",
            "pl": "Polish",
            "cs": "Czech",
            "tr": "Turkish",
            "el": "Greek",
            "he": "Hebrew",
            "id": "Indonesian",
            "hi": "Hindi",
            "th": "Thai",
        }

        lang = lang_map.get(lang_code, "Unknown")

        # Store the language globally for the conversation
        app.language = lang
        
        analysis = analyze_article_content(full_text, lang)
        
        return jsonify({'success': True, 'analysis': analysis})
    else:
        return jsonify({'success': False, 'error': 'Failed to process article'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    chat_history = data.get('chat_history', [])
    
    if not hasattr(app, 'vector_store'):
        return jsonify({'success': False, 'error': 'No article processed'})
    
    lang = getattr(app, 'language', 'en')
    
    try:
        # Convert chat history to LangChain format
        formatted_history = []
        for msg in chat_history:
            if msg['role'] == 'human':
                formatted_history.append(HumanMessage(content=msg['content']))
            else:
                formatted_history.append(AIMessage(content=msg['content']))
        
        retriever_chain = get_context_retriever_chain(app.vector_store, lang)
        if not retriever_chain:
            return jsonify({'success': False, 'response': 'Error processing request'})
            
        conversational_rag_chain = get_conversational_rag_chain(retriever_chain, lang)
        if not conversational_rag_chain:
            return jsonify({'success': False, 'response': 'Error processing request'})
            
        response = conversational_rag_chain.invoke({
            "chat_history": formatted_history,
            "input": message,
        })
        
        return jsonify({'success': True, 'response': response['answer']})
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return jsonify({'success': False, 'response': 'Error generating response'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)