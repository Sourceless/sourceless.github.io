(ns site-generator.core
  (:gen-class)
  (:require [clojure.string :as str]
            [clojure.edn :as edn]
            [markdown.core :as md]
            [selmer.parser :as sp]
            [selmer.util :as su]))

(def gen-dir (clojure.java.io/file "."))
(def posts-dir (clojure.java.io/file "posts"))
(def pages-dir (clojure.java.io/file "pages"))
(def assets-dir (clojure.java.io/file "assets"))
(def templates-dir (clojure.java.io/file "templates"))

(def url "file:///home/laurence/src/sourceless.github.io/dist")


(defn get-template [name]
  (slurp (str templates-dir "/" name ".html")))

(def post-template (get-template "post"))
(def page-template (get-template "page"))
(def footer-template (get-template "footer"))
(def header-template (get-template "header"))
(def index-template (get-template "index"))

(defn get-files-in-dir [path]
  (->> (clojure.java.io/file path)
       (file-seq)
       (filter #(.isFile %))))

(defn strip-dotpost [filename]
  (first
   (str/split
    (last (str/split filename #"\/"))
    #"\.")))

(defn parse-template [[filename content]]
  (let [parts (str/split content #"---")
        metadata (edn/read-string (first parts))
        markdown (md/md-to-html-string (last parts))]
    {:filename (strip-dotpost filename)
     :metadata metadata
     :content markdown}))

(defn get-posts [posts-dir]
  (let [post-files (get-files-in-dir posts-dir)
        post-contents (map vector (map str post-files) (map slurp post-files))]
    (map parse-template post-contents)))

(defn get-pages [pages-dir]
  (let [page-files (get-files-in-dir pages-dir)
        page-contents (map vector (map str page-files) (map slurp page-files))]
    (map parse-template page-contents)))

(defn format-inst [i]
  (.format (java.text.SimpleDateFormat. "yyyy-MM-dd") i))

(defn add-formatted-time [post]
  (into post {:formatted-date (format-inst (get-in post [:metadata :date]))}))

;; TODO: refactor
(defn render-post [post header footer]
  (let [current-year (str (.getYear (java.time.LocalDate/now)))]
    (su/without-escaping
     (sp/render post-template
                {:url url
                 :post (add-formatted-time post)
                 :current-year current-year
                 :header header
                 :footer footer}))))

(defn render-page [page header footer]
  (let [current-year (str (.getYear (java.time.LocalDate/now)))]
    (su/without-escaping
     (sp/render page-template
                {:url url
                 :page page
                 :current-year current-year
                 :header header
                 :footer footer}))))

(defn render-index-page [header posts]
  (let [current-year (str (.getYear (java.time.LocalDate/now)))
        sorted-posts (sort-by #(get-in % [:metadata :date]) posts)
        sorted-posts-with-rendered-time (doall (map add-formatted-time sorted-posts))]
    (su/without-escaping
     (sp/render index-template
                {:url url
                 :current-year current-year
                 :header header
                 :posts (reverse sorted-posts-with-rendered-time)}))))

;; TODO: refactor
(defn write-post [post header footer]
  (let [filename (str "./dist/posts/" (:filename post) ".html")]
    (println (str "Writing post " (:filename post) " to " filename))
    (spit filename
          (render-post post header footer))))

(defn write-page [page header footer]
  (let [filename (str "./dist/" (:filename page) ".html")]
    (println (str "Writing page " (:filename page) " to " filename))
    (spit filename
          (render-page page header footer))))

(defn write-index-page [header posts]
  (let [filename (str "./dist/index.html")]
    (println (str "Writing index to " filename))
    (spit filename
          (render-index-page header posts))))

(defn page-footer []
  (su/without-escaping
   (sp/render footer-template {})))

(defn get-post-date [p]
  (get-in p [:metadata :date]))

(defn post-footer [p posts]
  (let [posted-at (get-post-date p)
        posts-sorted (vec (sort-by get-post-date posts))
        sorted-dates (map get-post-date posts-sorted)
        date-index (.indexOf sorted-dates posted-at)
        prev-post (get posts-sorted (- date-index 1))
        next-post (get posts-sorted (+ date-index 1))]
    (su/without-escaping
     (sp/render footer-template
                {:url url
                 :prev-post prev-post
                 :next-post next-post}))))

(defn render-header [pages]
  (let [ordered-pages (sort-by #(get-in % [:metadata :order]) pages)]
    (su/without-escaping
     (sp/render header-template {:pages ordered-pages
                                 :url url}))))

;; TODO: pass in url at build time
;; TODO: Put this on gh actions/pages
;; TODO: unify templates so that there is a layout template
;; TODO: style improvements
(defn -main
  [& args]
  (clojure.java.io/make-parents "./dist/pages/.")
  (let [pages (get-pages pages-dir)
        posts (get-posts posts-dir)
        header (render-header pages)]
    (doseq [p pages]
      (let [footer (page-footer)]
        (write-page p header footer)))
    (doseq [p posts]
      (let [footer (post-footer p posts)]
        (write-post p header footer)))
    (write-index-page header posts)))
